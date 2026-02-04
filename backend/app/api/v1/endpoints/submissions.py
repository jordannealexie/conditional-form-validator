from app.services.form_validation import FormValidationService
from app.utils.queue import QueueService, send_submission_notification
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, UploadFile, File, Form
from app.models.user import User
from typing import Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.dependencies.auth import get_current_active_user, authorize
from app.schemas.forms import FormSubmissionCreate, FormSubmissionResponse, FormSubmissionListResponse, FormSubmissionUpdate, ValidationResult, ValidateSubmissionRequest, SubmissionReviewRequest
from app.repositories.forms import FormTemplateRepository, FormSubmissionRepository
from app.utils.response import create_response
from app import models, schemas
from app.models.forms import FormSubmission as FormSubmissionModel, SubmissionStatus
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from datetime import datetime, timezone
import json
from app.utils.minio import minio_client
from sqlalchemy.orm.attributes import flag_modified
import uuid as _uuid

router = APIRouter()


def _safe_filename(name: str) -> str:
    import os
    import re
    name = os.path.basename(name)
    return re.sub(r"[^\w\-_.]", "_", name)[:200]


async def _store_submission_files(
    db: AsyncSession,
    submission_id: int,
    data_json: dict,
    file_field_ids: List[str],
    files: List[UploadFile],
    current_user: User
) -> List[str]:
    """Store files only after submission and create DB records."""
    if not files:
        return []

    if len(files) != len(file_field_ids):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File field IDs do not match files")

    stored_objects: List[str] = []
    stored_tokens: List[str] = []

    try:
        for idx, upload in enumerate(files):
            field_id = file_field_ids[idx]
            if not upload.filename:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing filename")

            content = await upload.read()
            size = len(content)

            fname = _safe_filename(upload.filename)
            ts = int(datetime.now(timezone.utc).timestamp() * 1000)
            uid = str(_uuid.uuid4())[:8]
            object_name = f"file_{uid}_{ts}_{fname}"

            minio_client.upload_file(object_name, content, upload.content_type or "application/octet-stream")
            stored_objects.append(object_name)

            token_uuid = _uuid.uuid4()
            token_str = str(token_uuid)

            rec = models.forms.FormFile(
                token=token_uuid,
                original_filename=upload.filename,
                storage_path=object_name,
                mime_type=upload.content_type or "application/octet-stream",
                file_size=size,
                submission_id=submission_id,
                field_id=field_id,
                uploaded_by=current_user.username,
            )
            db.add(rec)

            data_json[field_id] = token_str
            stored_tokens.append(token_str)

        return stored_tokens
    except Exception as exc:
        for object_name in stored_objects:
            try:
                minio_client.delete_file(object_name)
            except Exception:
                pass
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to store files: {exc}")


def _can_access_submission(submission, user: User) -> bool:
    if getattr(user, 'is_superuser', False) or user.user_role == "admin":
        return True
    if user.user_role == "supervisor" and submission.template and submission.template.bank_id == user.bank_id:
        return True
    if submission.fieldman_id == user.username:
        return True
    return False

@router.post("/validate", response_model=ValidationResult)
async def validate_submission(
    request: ValidateSubmissionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Validate a form submission against its template schema.
    Does not save to database.
    
    STRICT VALIDATION RULES:
    - Required fields MUST have non-empty values
    - Empty values rejected: null, "", [], {}
    - Text fields CANNOT accept integers or floats
    - Numeric fields CANNOT accept strings
    - Date fields CANNOT accept numbers
    """
    template = await FormTemplateRepository.get_by_id(db, request.template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Form template not found"
        )
        
    # Convert SQLAlchemy model to dict for validation
    template_data = {
        "schema_json": template.schema_json,
        "fields": template.fields,
        "ui_schema": template.ui_schema
    }
    
    # Pass visible_fields to validation service if provided
    # This allows conditional fields to be excluded from required validation    
    result = FormValidationService.validate_submission(
        request.submission_data, 
        template_data,
        visible_fields=request.visible_fields
    )
    return create_response(data=result)

@router.post("/", response_model=FormSubmissionResponse)
async def create_submission(
    submission_in: FormSubmissionCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(authorize(resource="submissions", action="create"))
) -> Any:
    """Create a new form submission (Draft or Final).
    
    VALIDATION RULES (Backend-Enforced):
    - Required fields MUST have non-empty values
    - Empty values rejected: null, "", [], {}
    - Type mismatches rejected: text field cannot accept numbers
    - Submissions MUST pass validation to be saved as 'submitted'
    """
    template = await FormTemplateRepository.get_by_id(db, submission_in.template_id)
    if not template:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Form template not found")
    data_json = submission_in.submission_data if submission_in.submission_data is not None else submission_in.data_json
    if data_json is None:
        data_json = {}
    fieldman_id = submission_in.fieldman_id or current_user.username
    
    # Determine if this is a draft or final submission
    requested_status = (submission_in.status or "draft").lower()
    
    # Enforce ReBAC: If user is restricted to a bank, they can only submit for that bank
    # UNLESS they have explicit permissions (checked by authorize dependency)
    # Note: authorize(resource="submissions", action="create") already passed at this point,
    # so if user has the permission explicitly, we trust it.
    # Bank restriction is now optional/advisory, not blocking for users with permissions.
            
    template_data = {"schema_json": template.schema_json, "fields": template.fields, "ui_schema": template.ui_schema}
    
    # Pass visible_fields to validation service if provided
    # This allows conditional fields to be excluded from required validation
    validation_result = FormValidationService.validate_submission(
        data_json, 
        template_data,
        visible_fields=submission_in.visible_fields
    )
    
    # CRITICAL: For submitted submissions, validation MUST pass
    # Backend MUST reject submissions with empty required fields
    if requested_status == "submitted" and not validation_result.is_valid:
        error_details = [{"field": e.field, "message": e.message} for e in validation_result.errors]
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "message": "Submission validation failed. Required fields are missing or have invalid values.",
                "errors": error_details
            }
        )
    
    if submission_in.file_tokens:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File tokens are not supported. Submit files with the form submission."
        )

    if requested_status == "submitted":
        async with db.begin():
            submission = FormSubmissionModel(
                template_id=submission_in.template_id,
                fieldman_id=fieldman_id,
                submitted_by=current_user.id,
                data_json=data_json,
                file_tokens=[],
                status=requested_status,
                is_valid=validation_result.is_valid,
                validation_errors=[e.model_dump() for e in validation_result.errors] if validation_result.errors else [],
                submitted_at=datetime.now(timezone.utc)
            )
            db.add(submission)
            await db.flush()

        submission = await FormSubmissionRepository.get_by_id(db, submission.id)
        QueueService.enqueue(send_submission_notification, submission_id=submission.id, background_tasks=background_tasks)
        return create_response(data=FormSubmissionResponse.model_validate(submission))

    data = {
        "template_id": submission_in.template_id,
        "fieldman_id": fieldman_id,
        "submitted_by": current_user.id,
        "data_json": data_json,
        "file_tokens": [],
        "status": requested_status,
        "is_valid": validation_result.is_valid,
        "validation_errors": [e.model_dump() for e in validation_result.errors] if validation_result.errors else [],
        "submitted_at": None
    }
    submission = await FormSubmissionRepository.create(db, **data)
    submission = await FormSubmissionRepository.get_by_id(db, submission.id)
    QueueService.enqueue(send_submission_notification, submission_id=submission.id, background_tasks=background_tasks)
    return create_response(data=FormSubmissionResponse.model_validate(submission))


@router.post("/with-files", response_model=FormSubmissionResponse)
async def create_submission_with_files(
    template_id: int = Form(...),
    status_value: str = Form("submitted"),
    data_json_raw: str = Form(...),
    fieldman_id: Optional[str] = Form(None),
    file_field_ids: List[str] = Form(...),
    files: List[UploadFile] = File(...),
    background_tasks: BackgroundTasks = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(authorize(resource="submissions", action="create"))
) -> Any:
    """Create a submission with files. Files are stored only on submission."""
    if status_value.lower() != "submitted":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File uploads are only allowed on final submission")

    try:
        data_json = json.loads(data_json_raw)
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid data_json payload")

    template = await FormTemplateRepository.get_by_id(db, template_id)
    if not template:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Form template not found")

    template_data = {"schema_json": template.schema_json, "fields": template.fields, "ui_schema": template.ui_schema}
    validation_result = FormValidationService.validate_submission(data_json, template_data)
    if not validation_result.is_valid:
        error_details = [{"field": e.field, "message": e.message} for e in validation_result.errors]
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"message": "Submission validation failed.", "errors": error_details}
        )

    resolved_fieldman_id = fieldman_id or current_user.username

    try:
        submission = FormSubmissionModel(
            template_id=template_id,
            fieldman_id=resolved_fieldman_id,
            submitted_by=current_user.id,
            data_json=data_json,
            file_tokens=[],
            status="submitted",
            is_valid=validation_result.is_valid,
            validation_errors=[e.model_dump() for e in validation_result.errors] if validation_result.errors else [],
            submitted_at=datetime.now(timezone.utc)
        )
        db.add(submission)
        await db.flush()

        stored_tokens = await _store_submission_files(
            db=db,
            submission_id=submission.id,
            data_json=data_json,
            file_field_ids=file_field_ids,
            files=files,
            current_user=current_user
        )
        submission.file_tokens = stored_tokens
        submission.data_json = dict(data_json)
        flag_modified(submission, "data_json")

        await db.commit()
    except Exception as exc:
        await db.rollback()
        if isinstance(exc, HTTPException):
            raise exc
        raise

    submission = await FormSubmissionRepository.get_by_id(db, submission.id)
    if background_tasks:
        QueueService.enqueue(send_submission_notification, submission_id=submission.id, background_tasks=background_tasks)
    return create_response(data=FormSubmissionResponse.model_validate(submission))

@router.get("/", response_model=schemas.FormSubmissionListResponse)
async def list_submissions(
    page: int = 1,
    page_size: int = 20,
    status: Optional[str] = None,
    template_id: Optional[int] = None,
    bank_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(authorize(resource="submissions", action="read", alternate_actions=["viewDetails", "review"]))
) -> Any:
    """
    List form submissions. Permission-based access: submissions:read, submissions:viewDetails, or submissions:review
    """
    try:
        offset = (page - 1) * page_size
        
        # Use outerjoin instead of join to handle case when no submissions exist
        query = select(models.FormSubmission).options(
            selectinload(models.FormSubmission.template).selectinload(models.FormTemplate.bank)
        ).outerjoin(models.FormTemplate, models.FormSubmission.template_id == models.FormTemplate.id)
        
        # Filter by user role/bank
        # IMPORTANT: Submission visibility is PERMISSION-BASED, not ownership-based
        # Users with submissions:read/viewDetails/review can see ALL submissions
        # The authorize() dependency already verified they have the permission
        from app.core.casbin_enforcer import casbin_enforcer
        
        # Check if user has review or viewDetails permission (reviewers need to see all submissions)
        has_review_perm = casbin_enforcer.check_rbac_permission(current_user.username, "submissions", "review")
        has_view_details_perm = casbin_enforcer.check_rbac_permission(current_user.username, "submissions", "viewDetails")
        
        if getattr(current_user, 'is_superuser', False) or current_user.user_role == "admin":
            pass # Admin/Superuser sees all
        elif current_user.user_role == "supervisor":
            # Supervisor sees all in their bank
            if current_user.bank_id:
                query = query.where(models.FormTemplate.bank_id == current_user.bank_id)
        elif has_review_perm or has_view_details_perm:
            # Users with submissions:review or submissions:viewDetails can see ALL submissions
            # This is necessary for reviewers to do their job
            pass
        else:
            # Regular users without special permissions only see their own submissions
            query = query.where(models.FormSubmission.fieldman_id == current_user.username)
            
        # Additional filters
        if status:
            query = query.where(models.FormSubmission.status == status)
        if template_id:
            query = query.where(models.FormSubmission.template_id == template_id)
        if bank_id:
            query = query.where(models.FormTemplate.bank_id == bank_id)
            
        # Get total count using the same filters
        count_query = select(func.count(models.FormSubmission.id)).select_from(models.FormSubmission).outerjoin(models.FormTemplate, models.FormSubmission.template_id == models.FormTemplate.id)
        
        # Apply same filters to count query (must match main query logic)
        if getattr(current_user, 'is_superuser', False) or current_user.user_role == "admin":
            pass
        elif current_user.user_role == "supervisor" and current_user.bank_id:
            count_query = count_query.where(models.FormTemplate.bank_id == current_user.bank_id)
        elif has_review_perm or has_view_details_perm:
            # Users with review or viewDetails permission see all submissions
            pass
        else:
            count_query = count_query.where(models.FormSubmission.fieldman_id == current_user.username)
        
        if status:
            count_query = count_query.where(models.FormSubmission.status == status)
        if template_id:
            count_query = count_query.where(models.FormSubmission.template_id == template_id)
        if bank_id:
            count_query = count_query.where(models.FormTemplate.bank_id == bank_id)
        
        # Execute queries
        result = await db.execute(query.offset(offset).limit(page_size))
        submissions = result.scalars().all()
        
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0
        
        # Return proper format matching schema - use 'data' not 'items'
        return {
            "data": [FormSubmissionResponse.model_validate(s) for s in submissions],
            "total": total,
            "page": page,
            "page_size": page_size
        }
    except Exception as e:
        # Log the error for debugging
        import traceback
        print(f"Error loading submissions: {str(e)}")
        print(traceback.format_exc())
        
        # Return empty result instead of raising 500 error
        return {
            "data": [],
            "total": 0,
            "page": page,
            "page_size": page_size
        }


@router.get("/{id}", response_model=FormSubmissionResponse)
async def get_submission(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(authorize(resource="submissions", action="viewDetails", alternate_actions=["read", "review"]))
) -> Any:
    """Get a single submission. Permission-based access: submissions:viewDetails, submissions:read, or submissions:review"""
    submission = await FormSubmissionRepository.get_by_id(db, id)
    if not submission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found")
    # Authorization is handled by authorize() dependency - no need for ownership check
    # Users with proper permissions can view any submission
    return create_response(data=FormSubmissionResponse.model_validate(submission))


@router.put("/{id}", response_model=FormSubmissionResponse)
async def update_submission(
    id: int,
    body: FormSubmissionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(authorize(resource="submissions", action="update"))
) -> Any:
    """Update a draft submission.
    
    VALIDATION RULES (Backend-Enforced):
    - Only drafts can be updated
    - Only owner (fieldman) can update
    - If changing status to 'submitted', validation MUST pass
    - Required fields MUST have non-empty values
    """
    submission = await FormSubmissionRepository.get_by_id(db, id)
    if not submission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found")
    if submission.status != SubmissionStatus.DRAFT.value and submission.status != "draft":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only drafts can be updated")
    if submission.fieldman_id != current_user.username:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the owner can update this draft")
    upd = body.model_dump(exclude_unset=True)
    if upd:
        # Check if status is changing to submitted
        new_status = upd.get("status", submission.status)
        is_submitting = new_status and new_status.lower() == "submitted"
        
        # Re-validate if data_json changed or if submitting
        if ("data_json" in upd or is_submitting) and submission.template_id:
            t = await FormTemplateRepository.get_by_id(db, submission.template_id)
            if t:
                data_to_validate = upd.get("data_json", submission.data_json)
                res = FormValidationService.validate_submission(
                    data_to_validate, 
                    {"schema_json": t.schema_json, "fields": t.fields, "ui_schema": t.ui_schema}
                )
                upd["is_valid"] = res.is_valid
                upd["validation_errors"] = [e.model_dump() for e in res.errors] if res.errors else []
                
                # CRITICAL: If submitting, validation MUST pass
                if is_submitting and not res.is_valid:
                    error_details = [{"field": e.field, "message": e.message} for e in res.errors]
                    raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        detail={
                            "message": "Cannot submit: validation failed. Required fields are missing or have invalid values.",
                            "errors": error_details
                        }
                    )
                
                # Set submitted_at timestamp when submitting
                if is_submitting:
                    upd["submitted_at"] = datetime.now(timezone.utc)
        
        updated = await FormSubmissionRepository.update(db, submission, **upd)
        return create_response(data=FormSubmissionResponse.model_validate(updated))
    return create_response(data=FormSubmissionResponse.model_validate(submission))


@router.delete("/{id}")
async def delete_submission(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(authorize(resource="submissions", action="delete"))
) -> Any:
    """Delete own draft only."""
    submission = await FormSubmissionRepository.get_by_id(db, id)
    if not submission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found")
    if (submission.status or "").lower() != "draft":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only drafts can be deleted")
    if submission.fieldman_id != current_user.username:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the owner can delete this draft")
    await FormSubmissionRepository.delete(db, submission)
    return create_response(message="Submission deleted")


@router.post("/{id}/review", response_model=FormSubmissionResponse)
async def review_submission(
    id: int,
    body: SubmissionReviewRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(authorize(resource="submissions", action="review"))
) -> Any:
    """Approve or reject a submission.
    
    AUDIT FIELDS:
    - validated_by: Set to current user's username on approve/reject
    - validated_on: Set to current timestamp on approve/reject
    - reviewed_by: Also set for backwards compatibility
    - reviewed_at: Also set for backwards compatibility
    
    Permission-based: anyone with submissions:review can approve/reject any submission.
    """
    submission = await FormSubmissionRepository.get_by_id(db, id)
    if not submission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found")
    
    # Authorization is handled by authorize() dependency
    # Users with submissions:review permission can review ANY submission
    # No bank restrictions - permission is sufficient
    
    action = (body.action or "").lower()
    current_time = datetime.now(timezone.utc)
    
    if action == "approve":
        new_status = SubmissionStatus.VALIDATED.value
    elif action == "reject":
        new_status = SubmissionStatus.REJECTED.value
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="action must be 'approve' or 'reject'")
    
    # Update with all audit fields - both legacy and new
    await FormSubmissionRepository.update(
        db, 
        submission, 
        status=new_status,
        # Legacy audit fields (backwards compatible)
        reviewed_by=current_user.id,
        reviewed_at=current_time,
        reviewed_comment=body.comment,
        # New audit fields (per requirements)
        validated_by=current_user.id,
        validated_on=current_time
    )
    submission = await FormSubmissionRepository.get_by_id(db, id)
    return create_response(data=FormSubmissionResponse.model_validate(submission))

