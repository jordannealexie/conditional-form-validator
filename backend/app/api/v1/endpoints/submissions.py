from app.services.form_validation import FormValidationService
from app.utils.queue import QueueService, send_submission_notification
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
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

router = APIRouter()


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
        
    result = FormValidationService.validate_submission(request.submission_data, template_data)
    return create_response(data=result)

@router.post("/", response_model=FormSubmissionResponse)
async def create_submission(
    submission_in: FormSubmissionCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Create a new form submission (Draft or Final)."""
    template = await FormTemplateRepository.get_by_id(db, submission_in.template_id)
    if not template:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Form template not found")
    data_json = submission_in.submission_data if submission_in.submission_data is not None else submission_in.data_json
    if data_json is None:
        data_json = {}
    fieldman_id = submission_in.fieldman_id or current_user.username
    template_data = {"schema_json": template.schema_json, "fields": template.fields, "ui_schema": template.ui_schema}
    validation_result = FormValidationService.validate_submission(data_json, template_data)
    data = {
        "template_id": submission_in.template_id,
        "fieldman_id": fieldman_id,
        "data_json": data_json,
        "file_tokens": submission_in.file_tokens,
        "status": submission_in.status or "draft",
        "is_valid": validation_result.is_valid,
        "validation_errors": [e.model_dump() for e in validation_result.errors] if validation_result.errors else []
    }
    submission = await FormSubmissionRepository.create(db, **data)
    # Reload with relationships for the response
    submission = await FormSubmissionRepository.get_by_id(db, submission.id)
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
    current_user: models.User = Depends(get_current_active_user)
) -> Any:
    """
    List form submissions with role-based and bank-based filtering.
    """
    try:
        offset = (page - 1) * page_size
        
        # Use outerjoin instead of join to handle case when no submissions exist
        query = select(models.FormSubmission).options(
            selectinload(models.FormSubmission.template).selectinload(models.FormTemplate.bank)
        ).outerjoin(models.FormTemplate, models.FormSubmission.template_id == models.FormTemplate.id)
        
        # Filter by user role/bank
        if getattr(current_user, 'is_superuser', False) or current_user.user_role == "admin":
            pass # Admin/Superuser sees all
        elif current_user.user_role == "supervisor":
            # Supervisor sees all in their bank
            if current_user.bank_id:
                query = query.where(models.FormTemplate.bank_id == current_user.bank_id)
        else:
            # Fieldman sees only their own
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
        
        # Apply same filters to count query
        if getattr(current_user, 'is_superuser', False) or current_user.user_role == "admin":
            pass
        elif current_user.user_role == "supervisor" and current_user.bank_id:
            count_query = count_query.where(models.FormTemplate.bank_id == current_user.bank_id)
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
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Get a single submission. Access: own (fieldman), same bank (supervisor), all (admin)."""
    submission = await FormSubmissionRepository.get_by_id(db, id)
    if not submission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found")
    if not _can_access_submission(submission, current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to view this submission")
    return create_response(data=FormSubmissionResponse.model_validate(submission))


@router.put("/{id}", response_model=FormSubmissionResponse)
async def update_submission(
    id: int,
    body: FormSubmissionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Update a draft. Only owner (fieldman) can update."""
    submission = await FormSubmissionRepository.get_by_id(db, id)
    if not submission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found")
    if submission.status != SubmissionStatus.DRAFT.value and submission.status != "draft":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only drafts can be updated")
    if submission.fieldman_id != current_user.username:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the owner can update this draft")
    upd = body.model_dump(exclude_unset=True)
    if upd:
        # Re-validate if data_json changed
        if "data_json" in upd and submission.template_id:
            t = await FormTemplateRepository.get_by_id(db, submission.template_id)
            if t:
                res = FormValidationService.validate_submission(upd["data_json"], {"schema_json": t.schema_json, "fields": t.fields, "ui_schema": t.ui_schema})
                upd["is_valid"] = res.is_valid
                upd["validation_errors"] = [e.model_dump() for e in res.errors] if res.errors else []
        updated = await FormSubmissionRepository.update(db, submission, **upd)
        return create_response(data=FormSubmissionResponse.model_validate(updated))
    return create_response(data=FormSubmissionResponse.model_validate(submission))


@router.delete("/{id}")
async def delete_submission(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
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
    current_user: User = Depends(authorize(allowed_roles=["admin", "supervisor"]))
) -> Any:
    """Approve or reject. Supervisor: same bank only; Admin: all."""
    submission = await FormSubmissionRepository.get_by_id(db, id)
    if not submission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found")
    if current_user.user_role == "supervisor" and (not submission.template or submission.template.bank_id != current_user.bank_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to review submissions from another bank")
    action = (body.action or "").lower()
    if action == "approve":
        new_status = SubmissionStatus.VALIDATED.value
    elif action == "reject":
        new_status = SubmissionStatus.REJECTED.value
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="action must be 'approve' or 'reject'")
    await FormSubmissionRepository.update(db, submission, status=new_status, reviewed_by=current_user.username, reviewed_at=datetime.now(timezone.utc), reviewed_comment=body.comment)
    submission = await FormSubmissionRepository.get_by_id(db, id)
    return create_response(data=FormSubmissionResponse.model_validate(submission))

