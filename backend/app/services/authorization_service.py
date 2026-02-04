"""
Unified Authorization Service - Combines RBAC and ABAC
"""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.services.abac_service import ABACService
from app.core.casbin_enforcer import casbin_enforcer
from app.schemas.authorization import AuthorizationModel, AuthorizationResult


class AuthorizationService:
    """Unified authorization service that combines RBAC and ABAC"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.abac_service = ABACService(db)
    
    async def check_permission(
        self,
        user: User,
        resource: str,
        action: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None
    ) -> tuple[bool, List[AuthorizationModel], List[AuthorizationResult]]:
        """
        Check permission across RBAC and ABAC
        Returns: (has_permission, granted_by_models, detailed_results)
        """
        results = []
        granted_by = []
        
        # 1. Check RBAC
        rbac_permission = await casbin_enforcer.check_rbac_permission_async(
            user.username, resource, action
        )
        results.append(AuthorizationResult(
            model=AuthorizationModel.RBAC,
            has_permission=rbac_permission,
            reason="Role-based access control check"
        ))
        if rbac_permission:
            granted_by.append(AuthorizationModel.RBAC)
        else:
            # RBAC failed - deny immediately
            return False, granted_by, results
        
        # 2. Check ABAC
        abac_permission, matched_policies, failed_policies = await self.abac_service.evaluate_policy(
            user, resource, action, resource_type, resource_id
        )
        if failed_policies:
            reason = f"Failed policies: {', '.join(failed_policies)}"
        elif matched_policies:
            reason = f"Matched policies: {', '.join(matched_policies)}"
        else:
            reason = "No applicable policies"
        results.append(AuthorizationResult(
            model=AuthorizationModel.ABAC,
            has_permission=abac_permission,
            reason=reason
        ))
        if abac_permission:
            granted_by.append(AuthorizationModel.ABAC)

        # Permission granted only if RBAC and ABAC both allow
        return abac_permission, granted_by, results
