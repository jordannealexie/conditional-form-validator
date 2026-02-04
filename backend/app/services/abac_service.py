"""
ABAC Service - Attribute-Based Access Control operations
"""
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.abac import UserAttribute, ResourceAttribute, ABACPolicy
from app.models.user import User


class ABACService:
    """Service for managing ABAC policies and attributes"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    # Policy Management
    async def create_policy(
        self,
        name: str,
        description: Optional[str],
        rules: Dict[str, Any],
        is_active: bool = True
    ) -> ABACPolicy:
        """Create a new ABAC policy"""
        policy = ABACPolicy(
            name=name,
            description=description,
            rules=rules,
            is_active=is_active
        )
        self.db.add(policy)
        await self.db.commit()
        await self.db.refresh(policy)
        
        # Sync to Casbin if active
        if is_active:
            await self.sync_policy_to_casbin(policy)
        
        return policy
    
    async def get_policies(self, active_only: bool = False) -> List[ABACPolicy]:
        """Get all ABAC policies"""
        query = select(ABACPolicy)
        if active_only:
            query = query.where(ABACPolicy.is_active == True)
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_policy(self, policy_id: int) -> Optional[ABACPolicy]:
        """Get a specific policy by ID"""
        result = await self.db.execute(
            select(ABACPolicy).where(ABACPolicy.id == policy_id)
        )
        return result.scalar_one_or_none()
    
    async def update_policy(
        self,
        policy_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        rules: Optional[Dict[str, Any]] = None,
        is_active: Optional[bool] = None
    ) -> Optional[ABACPolicy]:
        """Update an existing ABAC policy"""
        from datetime import datetime, timezone
        
        policy = await self.get_policy(policy_id)
        if not policy:
            return None
        
        if name is not None:
            policy.name = name
        if description is not None:
            policy.description = description
        if rules is not None:
            policy.rules = rules
        if is_active is not None:
            policy.is_active = is_active
        
        # Explicitly set updated_at with timezone
        policy.updated_at = datetime.now(timezone.utc)
        
        await self.db.commit()
        await self.db.refresh(policy)
        
        # Sync to Casbin if active
        if policy.is_active:
            await self.sync_policy_to_casbin(policy)
        
        return policy
    
    async def delete_policy(self, policy_id: int) -> bool:
        """Delete an ABAC policy"""
        policy = await self.get_policy(policy_id)
        if not policy:
            return False
        
        await self.db.delete(policy)
        await self.db.commit()
        return True
    
    # User Attribute Management
    async def set_user_attribute(
        self,
        user_id: int,
        attribute_key: str,
        attribute_value: str
    ) -> UserAttribute:
        """Set or update a user attribute"""
        # Check if attribute exists
        result = await self.db.execute(
            select(UserAttribute).where(
                UserAttribute.user_id == user_id,
                UserAttribute.attribute_key == attribute_key
            )
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            existing.attribute_value = attribute_value
            await self.db.commit()
            await self.db.refresh(existing)
            return existing
        else:
            attribute = UserAttribute(
                user_id=user_id,
                attribute_key=attribute_key,
                attribute_value=attribute_value
            )
            self.db.add(attribute)
            await self.db.commit()
            await self.db.refresh(attribute)
            return attribute
    
    async def get_user_attributes(self, user_id: int) -> List[UserAttribute]:
        """Get all attributes for a user"""
        result = await self.db.execute(
            select(UserAttribute).where(UserAttribute.user_id == user_id)
        )
        return list(result.scalars().all())
    
    async def get_user_attributes_dict(self, user_id: int) -> Dict[str, str]:
        """Get user attributes as a dictionary"""
        attributes = await self.get_user_attributes(user_id)
        return {attr.attribute_key: attr.attribute_value for attr in attributes}
    
    # Resource Attribute Management
    async def set_resource_attribute(
        self,
        resource_type: str,
        resource_id: str,
        attribute_key: str,
        attribute_value: str
    ) -> ResourceAttribute:
        """Set or update a resource attribute"""
        # Check if attribute exists
        result = await self.db.execute(
            select(ResourceAttribute).where(
                ResourceAttribute.resource_type == resource_type,
                ResourceAttribute.resource_id == resource_id,
                ResourceAttribute.attribute_key == attribute_key
            )
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            existing.attribute_value = attribute_value
            await self.db.commit()
            await self.db.refresh(existing)
            return existing
        else:
            attribute = ResourceAttribute(
                resource_type=resource_type,
                resource_id=resource_id,
                attribute_key=attribute_key,
                attribute_value=attribute_value
            )
            self.db.add(attribute)
            await self.db.commit()
            await self.db.refresh(attribute)
            return attribute
    
    async def get_resource_attributes(
        self,
        resource_type: str,
        resource_id: str
    ) -> List[ResourceAttribute]:
        """Get all attributes for a resource"""
        result = await self.db.execute(
            select(ResourceAttribute).where(
                ResourceAttribute.resource_type == resource_type,
                ResourceAttribute.resource_id == resource_id
            )
        )
        return list(result.scalars().all())
    
    async def get_resource_attributes_dict(
        self,
        resource_type: str,
        resource_id: str
    ) -> Dict[str, str]:
        """Get resource attributes as a dictionary"""
        attributes = await self.get_resource_attributes(resource_type, resource_id)
        return {attr.attribute_key: attr.attribute_value for attr in attributes}
    
    # Policy Evaluation
    async def evaluate_policy(
        self,
        user: User,
        resource: str,
        action: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        resource_attrs_override: Optional[Dict[str, Any]] = None,
        env_attrs_override: Optional[Dict[str, Any]] = None
    ) -> tuple[bool, List[str], List[str]]:
        """
        Evaluate ABAC policies for a user
        Returns: (has_permission, matched_policy_names, failed_policy_names)
        """
        # Gather user attributes
        user_attrs = {
            "user_id": user.id,
            "roles": [r.name for r in getattr(user, "roles", [])] if getattr(user, "roles", None) else [],
            "department": user.department or "",
            "account_status": "active" if user.active else "inactive",
            "location": user.location or "",
            "level": user.level or 1,
            "bank_id": getattr(user, "bank_id", None),
            "is_superuser": user.is_superuser,
        }
        
        # Add custom attributes
        custom_attrs = await self.get_user_attributes_dict(user.id)
        user_attrs.update(custom_attrs)
        
        # Gather resource attributes if provided
        resource_attrs = resource_attrs_override or {}
        if not resource_attrs and resource_type and resource_id:
            resource_attrs = await self.get_resource_attributes_dict(resource_type, resource_id)
        
        # Environment attributes
        env_attrs = env_attrs_override or {
            "time": None,
            "request_origin": None,
        }

        # Get active policies
        policies = await self.get_policies(active_only=True)
        matched_policies = []
        failed_policies = []

        # Evaluate each policy that targets this resource/action
        for policy in policies:
            is_applicable, is_allowed = self._evaluate_policy_rules(
                policy.rules,
                user_attrs,
                resource_attrs,
                env_attrs,
                resource,
                action
            )
            if not is_applicable:
                continue
            if is_allowed:
                matched_policies.append(policy.name)
            else:
                failed_policies.append(policy.name)

        # If no applicable policies, allow (RBAC already passed)
        if not matched_policies and not failed_policies:
            return True, [], []

        # Allow if at least one policy matched and no policies explicitly denied
        # This is "permit-override" semantics - any explicit allow wins
        if matched_policies and not failed_policies:
            return True, matched_policies, []
        
        # Deny if any applicable policy explicitly denies
        has_permission = len(failed_policies) == 0
        return has_permission, matched_policies, failed_policies
    
    def _evaluate_policy_rules(
        self,
        rules: Dict[str, Any],
        user_attrs: Dict[str, Any],
        resource_attrs: Dict[str, Any],
        env_attrs: Dict[str, Any],
        resource: str,
        action: str
    ) -> tuple[bool, bool]:
        """Evaluate policy rules against attributes.

        Returns (is_applicable, is_allowed).
        """
        # Check if permissions match
        perms = rules.get("permissions", {})
        
        # Handle permissions as a list of {resource, action} objects
        if isinstance(perms, list):
            is_applicable = any(
                p.get("resource") == resource and p.get("action") == action
                for p in perms
            )
            if not is_applicable:
                return False, False
        else:
            # Handle permissions as a single object with resource and action
            perm_resource = perms.get("resource")
            perm_action = perms.get("action")
            
            # action can be a string or a list
            if perm_resource != resource:
                return False, False
            if isinstance(perm_action, list):
                if action not in perm_action:
                    return False, False
            elif perm_action != action:
                return False, False

        # Check conditions
        conditions = rules.get("conditions", [])
        for condition in conditions:
            attr_name = condition.get("attribute")
            operator = condition.get("operator")
            expected_value = condition.get("value")

            actual_value = self._resolve_attribute_value(
                attr_name,
                user_attrs=user_attrs,
                resource_attrs=resource_attrs,
                env_attrs=env_attrs,
                action_value=action
            )

            if not self._compare_values(actual_value, operator, expected_value):
                # Role-based conditions (user.roles, user.role) determine applicability
                # If user doesn't match the role condition, policy is not applicable to them
                if attr_name in ("user.roles", "user.role", "subject.roles", "subject.role"):
                    return False, False  # Not applicable
                # Other conditions that fail mean policy applies but denies
                return True, False

        return True, True

    def _resolve_attribute_value(
        self,
        attr_name: str,
        user_attrs: Dict[str, Any],
        resource_attrs: Dict[str, Any],
        env_attrs: Dict[str, Any],
        action_value: str
    ) -> Any:
        if not attr_name:
            return None

        if attr_name.startswith("subject."):
            return user_attrs.get(attr_name.replace("subject.", "", 1))
        if attr_name.startswith("user."):
            return user_attrs.get(attr_name.replace("user.", "", 1))
        if attr_name.startswith("resource."):
            return resource_attrs.get(attr_name.replace("resource.", "", 1))
        if attr_name.startswith("env."):
            return env_attrs.get(attr_name.replace("env.", "", 1))
        if attr_name == "action":
            return action_value

        return user_attrs.get(attr_name) or resource_attrs.get(attr_name) or env_attrs.get(attr_name)
    
    def _compare_values(self, actual: Any, operator: str, expected: Any) -> bool:
        """Compare values based on operator"""
        try:
            if operator == "equals" or operator == "==":
                return str(actual) == str(expected)
            elif operator == "!=":
                return str(actual) != str(expected)
            elif operator == ">":
                return float(actual) > float(expected)
            elif operator == ">=":
                return float(actual) >= float(expected)
            elif operator == "<":
                return float(actual) < float(expected)
            elif operator == "<=":
                return float(actual) <= float(expected)
            elif operator == "in":
                if isinstance(actual, (list, tuple, set)):
                    return expected in actual or str(expected) in [str(v) for v in actual]
                return str(actual) in expected
            elif operator == "not_in":
                if isinstance(actual, (list, tuple, set)):
                    return expected not in actual and str(expected) not in [str(v) for v in actual]
                return str(actual) not in expected
            elif operator == "contains":
                if isinstance(actual, (list, tuple, set)):
                    return expected in actual or str(expected) in [str(v) for v in actual]
                return str(expected) in str(actual)
            elif operator == "startswith":
                return str(actual).startswith(str(expected))
            elif operator == "endswith":
                return str(actual).endswith(str(expected))
            else:
                return False
        except (ValueError, TypeError):
            return False
    
    async def sync_policy_to_casbin(self, policy: ABACPolicy):
        """Sync policy to Casbin enforcer (if needed for complex rules)"""
        # For now, Casbin uses the matcher in abac_model.conf
        # This could be used to add specific rules to Casbin if needed
        pass
