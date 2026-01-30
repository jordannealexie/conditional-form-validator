"""
ReBAC API endpoints
"""
from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, distinct
from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.dependencies.permissions import require_permission, require_any_permission
from app.models.user import User
from app.schemas.rbac import (
    ResourceRelationshipCreate,
    ResourceRelationshipResponse,
    REBACCheckRequest,
    REBACCheckResponse
)
from app.services.rebac_service import REBACService
from app.utils.response import create_response

router = APIRouter()


@router.post("/relationships", response_model=ResourceRelationshipResponse, status_code=status.HTTP_201_CREATED)
async def create_relationship(
    relationship_data: ResourceRelationshipCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("relationships:create"))
):
    """Create a new resource relationship - requires relationships:create permission"""
    service = REBACService(db)
    relationship = await service.create_relationship(
        subject_type=relationship_data.subject_type,
        subject_id=relationship_data.subject_id,
        resource_type=relationship_data.resource_type,
        resource_id=relationship_data.resource_id,
        parent_resource_type=relationship_data.parent_resource_type,
        parent_resource_id=relationship_data.parent_resource_id,
        relationship_type=relationship_data.relationship_type
    )
    return create_response(data=ResourceRelationshipResponse.model_validate(relationship), status_code=status.HTTP_201_CREATED)


@router.get("/relationships", response_model=List[ResourceRelationshipResponse])
async def list_relationships(
    subject_type: Optional[str] = None,
    subject_id: Optional[str] = None,
    resource_type: Optional[str] = None,
    resource_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("relationships:read"))
):
    """List all relationships with optional filters - requires relationships:read permission"""
    service = REBACService(db)
    relationships = await service.get_relationships(
        subject_type=subject_type,
        subject_id=subject_id,
        resource_type=resource_type,
        resource_id=resource_id
    )
    data = [ResourceRelationshipResponse.model_validate(r) for r in relationships]
    return create_response(data=data)


@router.delete("/relationships/{relationship_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_relationship(
    relationship_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("relationships:delete"))
):
    """Delete a relationship - requires relationships:delete permission"""
    service = REBACService(db)
    success = await service.delete_relationship(relationship_id)
    if not success:
        raise HTTPException(status_code=404, detail="Relationship not found")
    return None


@router.get("/relationships/resource/{resource_type}/{resource_id}", response_model=List[ResourceRelationshipResponse])
async def get_resource_relationships(
    resource_type: str,
    resource_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all relationships for a specific resource"""
    service = REBACService(db)
    relationships = await service.get_relationships(
        resource_type=resource_type,
        resource_id=resource_id
    )
    data = [ResourceRelationshipResponse.model_validate(r) for r in relationships]
    return create_response(data=data)


@router.post("/check", response_model=REBACCheckResponse)
async def check_rebac_permission(
    check_request: REBACCheckRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Check if a user has permission based on relationships"""
    service = REBACService(db)
    has_permission, relationship_path = await service.check_access_path(
        username=check_request.username,
        resource=check_request.resource,
        action=check_request.action
    )
    
    reason = "Access granted via relationship chain" if has_permission else "No valid relationship path found"
    
    return REBACCheckResponse(
        username=check_request.username,
        resource=check_request.resource,
        action=check_request.action,
        has_permission=has_permission,
        relationship_path=relationship_path,
        reason=reason
    )

@router.put("/relationships/{relationship_id}", response_model=ResourceRelationshipResponse)
async def update_relationship(
    relationship_id: int,
    relationship_data: ResourceRelationshipCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("relationships:update"))
):
    """Update a relationship - requires relationships:update permission"""
    service = REBACService(db)
    
    # Check existence
    # We can add an update method to service
    updated = await service.update_relationship(
        relationship_id,
        relationship_type=relationship_data.relationship_type,
        # Potentially allow updating other fields if needed, but usually just type changes.
        # However, the UI might send all fields.
        subject_type=relationship_data.subject_type,
        subject_id=relationship_data.subject_id,
        resource_type=relationship_data.resource_type,
        resource_id=relationship_data.resource_id,
        parent_resource_type=relationship_data.parent_resource_type,
        parent_resource_id=relationship_data.parent_resource_id
    )
    
    if not updated:
        raise HTTPException(status_code=404, detail="Relationship not found")
        
    return create_response(data=ResourceRelationshipResponse.model_validate(updated))


@router.get("/metadata/options")
async def get_rebac_options(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_any_permission("relationships:read", "relationships:create", "relationships:update"))
):
    """Get available options for ReBAC relationship creation - requires any relationships permission"""
    from app.models.user import ResourceRelationship
    from app.models.forms import FormTemplate, FormSubmission, Bank
    from app.models.user import User as UserModel, Role
    
    # Get distinct values from existing relationships
    subject_types_result = await db.execute(
        select(distinct(ResourceRelationship.subject_type))
    )
    subject_types_from_db = [row[0] for row in subject_types_result.fetchall() if row[0]]
    
    resource_types_result = await db.execute(
        select(distinct(ResourceRelationship.resource_type))
    )
    resource_types_from_db = [row[0] for row in resource_types_result.fetchall() if row[0]]
    
    relationship_types_result = await db.execute(
        select(distinct(ResourceRelationship.relationship_type))
    )
    relationship_types_from_db = [row[0] for row in relationship_types_result.fetchall() if row[0]]
    
    # Combine with standard entity types
    subject_types = list(set(["user", "role", "group"] + subject_types_from_db))
    resource_types = list(set(["template", "submission", "bank", "document", "project"] + resource_types_from_db))
    relationship_types = list(set(["owner", "viewer", "editor", "manager", "member", "admin", "creator", "assignee", "reviewer"] + relationship_types_from_db))
    
    # Get actual entities for dropdowns
    users_result = await db.execute(select(UserModel.id, UserModel.username).limit(100))
    users = [{"id": str(row[0]), "label": row[1]} for row in users_result.fetchall()]
    
    roles_result = await db.execute(select(Role.id, Role.name).limit(50))
    roles = [{"id": str(row[0]), "label": row[1]} for row in roles_result.fetchall()]
    
    templates_result = await db.execute(select(FormTemplate.id, FormTemplate.name).limit(100))
    templates = [{"id": str(row[0]), "label": row[1]} for row in templates_result.fetchall()]
    
    submissions_result = await db.execute(select(FormSubmission.id, FormSubmission.submitted_by).limit(100))
    submissions = [{"id": str(row[0]), "label": f"Submission #{row[0]}"} for row in submissions_result.fetchall()]
    
    banks_result = await db.execute(select(Bank.id, Bank.name).limit(50))
    banks = [{"id": str(row[0]), "label": row[1]} for row in banks_result.fetchall()]
    
    return create_response(data={
        "subject_types": sorted(subject_types),
        "resource_types": sorted(resource_types),
        "relationship_types": sorted(relationship_types),
        "entities": {
            "users": users,
            "roles": roles,
            "templates": templates,
            "submissions": submissions,
            "banks": banks
        }
    })
