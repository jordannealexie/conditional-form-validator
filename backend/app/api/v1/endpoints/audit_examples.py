"""
Example implementation of bulk audit logging in user endpoints.

This file demonstrates how to integrate bulk audit logging into existing endpoints.
Copy these patterns into your actual endpoint files.
"""

from typing import List
from fastapi import APIRouter, Depends, Request
from app.dependencies.auth import get_current_active_user, authorize
from app.dependencies.services import get_user_service
from app.dependencies.audit import get_bulk_audit_service
from app.services.user_service import UserService
from app.services.bulk_audit import BulkAuditService
from app.models.user import User
from app.schemas.auth import UserCreate, UserResponse
from app.utils.response import create_response
from app.dtos.custom_response_dto import CustomResponse

router = APIRouter()


@router.post(
    "/users/bulk-create-example",
    response_model=CustomResponse[List[UserResponse]],
    summary="Bulk create users with audit logging (EXAMPLE)",
    description="Example of how to implement bulk user creation with proper audit logging"
)
async def bulk_create_users_example(
    users_data: List[UserCreate],
    request: Request,
    current_user: User = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user_service),
    bulk_audit_service: BulkAuditService = Depends(get_bulk_audit_service),
):
    """
    Example: Bulk create users with audit logging.
    
    Key Points:
    1. Use BulkAuditCollector context manager
    2. Collect all audit entries in memory
    3. Single bulk insert dispatched to Celery on context exit
    4. Business logic completes immediately
    """
    
    created_users = []
    
    # Create bulk audit collector
    async with bulk_audit_service.create_collector() as collector:
        # Process each user
        for user_data in users_data:
            # Business logic: create user
            user = await user_service.create_user(user_data)
            created_users.append(user)
            
            # Audit: Add entry to collector (NOT yet persisted)
            collector.add_entry(
                action="created",
                entity_type="user",
                entity_id=user.id,
                actor_user_id=current_user.id,
                actor_username=current_user.username,
                after_json={
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "is_active": user.is_active,
                    "role": user.role,
                },
                request=request  # Automatically extracts IP and user agent
            )
    
    # At this point:
    # - All audit entries are dispatched to Celery for bulk insert
    # - Business logic continues immediately without blocking
    # - Celery worker will perform bulk INSERT in background
    
    return create_response(
        data=[UserResponse.model_validate(u) for u in created_users],
        message=f"Successfully created {len(created_users)} users"
    )


@router.put(
    "/users/bulk-update-example",
    response_model=CustomResponse[List[UserResponse]],
    summary="Bulk update users with audit logging (EXAMPLE)",
    description="Example of how to implement bulk user updates with proper audit logging"
)
async def bulk_update_users_example(
    updates: List[dict],  # In reality, use proper Pydantic schema
    request: Request,
    current_user: User = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user_service),
    bulk_audit_service: BulkAuditService = Depends(get_bulk_audit_service),
):
    """
    Example: Bulk update users with before/after audit logging.
    
    Key Points:
    1. Capture BEFORE state before making changes
    2. Apply updates
    3. Capture AFTER state
    4. Calculate edited_fields
    5. Add to bulk collector
    """
    
    updated_users = []
    
    async with bulk_audit_service.create_collector() as collector:
        for update_data in updates:
            user_id = update_data.get("user_id")
            
            # Get current state (BEFORE)
            user = await user_service.get(user_id)
            if not user:
                continue
            
            before_state = {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "is_active": user.is_active,
                "role": user.role,
            }
            
            # Business logic: update user
            updated_user = await user_service.update(user_id, update_data)
            updated_users.append(updated_user)
            
            # Get new state (AFTER)
            after_state = {
                "id": updated_user.id,
                "username": updated_user.username,
                "email": updated_user.email,
                "is_active": updated_user.is_active,
                "role": updated_user.role,
            }
            
            # Calculate which fields changed
            edited_fields = [
                key for key in before_state.keys()
                if before_state.get(key) != after_state.get(key)
            ]
            
            # Audit: Add entry with before/after
            collector.add_entry(
                action="updated",
                entity_type="user",
                entity_id=updated_user.id,
                actor_user_id=current_user.id,
                actor_username=current_user.username,
                before_json=before_state,
                after_json=after_state,
                edited_fields=edited_fields,
                request=request
            )
    
    return create_response(
        data=[UserResponse.model_validate(u) for u in updated_users],
        message=f"Successfully updated {len(updated_users)} users"
    )


@router.delete(
    "/users/bulk-delete-example",
    response_model=CustomResponse[dict],
    summary="Bulk delete users with audit logging (EXAMPLE)",
    description="Example of how to implement bulk user deletion with proper audit logging"
)
async def bulk_delete_users_example(
    user_ids: List[int],
    request: Request,
    current_user: User = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user_service),
    bulk_audit_service: BulkAuditService = Depends(get_bulk_audit_service),
):
    """
    Example: Bulk delete users with audit logging.
    
    Key Points:
    1. Capture state BEFORE deletion
    2. Delete the entity
    3. Log with before_json (no after_json for deletes)
    """
    
    deleted_count = 0
    
    async with bulk_audit_service.create_collector() as collector:
        for user_id in user_ids:
            # Get user before deletion (BEFORE)
            user = await user_service.get(user_id)
            if not user:
                continue
            
            before_state = {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "is_active": user.is_active,
                "role": user.role,
            }
            
            # Business logic: delete user
            await user_service.delete(user_id)
            deleted_count += 1
            
            # Audit: Add entry with before state only
            collector.add_entry(
                action="deleted",
                entity_type="user",
                entity_id=user_id,
                actor_user_id=current_user.id,
                actor_username=current_user.username,
                before_json=before_state,
                # NO after_json for deletions
                request=request
            )
    
    return create_response(
        data={"deleted_count": deleted_count},
        message=f"Successfully deleted {deleted_count} users"
    )


# ============================================================================
# SINGLE ENTITY OPERATIONS (still use bulk collector for consistency)
# ============================================================================

@router.post(
    "/users/single-create-example",
    response_model=CustomResponse[UserResponse],
    summary="Create single user with audit logging (EXAMPLE)",
    description="Even for single operations, use bulk collector for consistency"
)
async def create_single_user_example(
    user_data: UserCreate,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user_service),
    bulk_audit_service: BulkAuditService = Depends(get_bulk_audit_service),
):
    """
    Example: Create single user.
    
    Even for single entities, use the bulk collector for consistency.
    The collector will still dispatch to Celery (async) with 1 entry.
    """
    
    async with bulk_audit_service.create_collector() as collector:
        # Create user
        user = await user_service.create_user(user_data)
        
        # Add audit entry
        collector.add_entry(
            action="created",
            entity_type="user",
            entity_id=user.id,
            actor_user_id=current_user.id,
            actor_username=current_user.username,
            after_json={
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "is_active": user.is_active,
            },
            request=request
        )
    
    return create_response(
        data=UserResponse.model_validate(user),
        message="User created successfully"
    )


# ============================================================================
# PATTERN FOR ROLES
# ============================================================================

@router.post(
    "/roles/bulk-create-example",
    summary="Bulk create roles with audit logging (EXAMPLE)",
)
async def bulk_create_roles_example(
    roles_data: List[dict],
    request: Request,
    current_user: User = Depends(get_current_active_user),
    bulk_audit_service: BulkAuditService = Depends(get_bulk_audit_service),
):
    """
    Example: Same pattern works for any entity type.
    
    Just change:
    - entity_type="role"
    - Business logic for role creation
    """
    
    created_roles = []
    
    async with bulk_audit_service.create_collector() as collector:
        for role_data in roles_data:
            # Business logic: create role
            # role = await role_service.create(role_data)
            # created_roles.append(role)
            
            # Audit
            # collector.add_entry(
            #     action="created",
            #     entity_type="role",  # <-- Change entity type
            #     entity_id=role.id,
            #     actor_user_id=current_user.id,
            #     actor_username=current_user.username,
            #     after_json={...},
            #     request=request
            # )
            pass
    
    return create_response(message="Pattern demonstration")


# ============================================================================
# PATTERN FOR FORM TEMPLATES
# ============================================================================

@router.post(
    "/form-templates/bulk-create-example",
    summary="Bulk create form templates with audit logging (EXAMPLE)",
)
async def bulk_create_templates_example(
    templates_data: List[dict],
    request: Request,
    current_user: User = Depends(get_current_active_user),
    bulk_audit_service: BulkAuditService = Depends(get_bulk_audit_service),
):
    """
    Example: Same pattern for form templates.
    
    Just change:
    - entity_type="form_template"
    - Business logic for template creation
    """
    
    created_templates = []
    
    async with bulk_audit_service.create_collector() as collector:
        for template_data in templates_data:
            # Business logic: create template
            # template = await template_service.create(template_data)
            # created_templates.append(template)
            
            # Audit
            # collector.add_entry(
            #     action="created",
            #     entity_type="form_template",  # <-- Change entity type
            #     entity_id=template.id,
            #     actor_user_id=current_user.id,
            #     actor_username=current_user.username,
            #     after_json={...},
            #     request=request
            # )
            pass
    
    return create_response(message="Pattern demonstration")
