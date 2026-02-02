from typing import List, Optional, Union

import asyncio
from app.core.security import get_password_hash
from app.core.casbin_enforcer import casbin_enforcer
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate, UserUpdate
from app.schemas.auth import UserCreate as AuthUserCreate
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from app.models.user import Role, user_roles
from app.models.audit import AuditLog
from sqlalchemy.exc import IntegrityError

class UserService:    

    def __init__(self, db: AsyncSession, user_repo: UserRepository):
        """Initialize with user repository"""
        self.db = db
        self.user_repo = user_repo

    async def create_admin_user(self, inp: AuthUserCreate) -> User:
        """Create user from admin (auth.UserCreate with user_role, bank_id)."""
        try:
            data = {
                "username": inp.username,
                "email": inp.email,
                "password_hash": get_password_hash(inp.password),
                "user_role": inp.user_role or "fieldman",
                "bank_id": inp.bank_id,
                "active": True,
                "first_name": inp.first_name,
                "last_name": inp.last_name,
                "full_name": inp.full_name or " ".join([p for p in [inp.first_name, inp.last_name] if p]).strip() or None,
                "department": inp.department,
                "level": inp.level or 1,
                "location": inp.location,
            }
            # Don't commit - let endpoint handle commit after audit logging
            user = await self.user_repo.create(obj_in=data, commit_txn=False)
            
            # Sync roles
            if user.user_role:
                stmt = select(Role).where(Role.name == user.user_role)
                result = await self.db.execute(stmt)
                role_obj = result.scalar_one_or_none()
                if role_obj:
                    # Use insert statement properly
                    insert_stmt = user_roles.insert().values(user_id=user.id, role_id=role_obj.id)
                    await self.db.execute(insert_stmt)
                    
                    # Sync to Casbin (run in threadpool since Casbin is synchronous)
                    loop = asyncio.get_event_loop()
                    await loop.run_in_executor(None, casbin_enforcer.sync_user_roles, user.username, [role_obj.name])
            
            # Flush to get ID and updated data but don't commit yet
            await self.db.flush()
            await self.db.refresh(user)

            return user
        except IntegrityError as e:
            await self.db.rollback()
            error_msg = str(e.orig) if hasattr(e, 'orig') else str(e)
            if "unique constraint" in error_msg.lower():
                if "email" in error_msg.lower():
                    raise Exception("Email already registered")
                elif "username" in error_msg.lower():
                    raise Exception("Username already taken")
            raise Exception(f"Failed to create user: {error_msg}")
        except Exception as e:
            await self.db.rollback()
            raise

    async def get(self, user_id: int) -> Optional[User]:
        """Get a user by ID"""
        result = await self.user_repo.get(user_id)
        # attach casbin role if available (run sync casbin calls in executor)
        try:
            if result:
                loop = asyncio.get_event_loop()
                roles = await loop.run_in_executor(None, casbin_enforcer.get_roles_for_user, result.username)
                if roles:
                    result._casbin_role = roles[0]
        except Exception:
            # enforcer may not be initialized yet; leave DB role/property as-is
            pass
        return result

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get a user by email"""
        result = await self.user_repo.get_by_email(email)
        try:
            if result:
                loop = asyncio.get_event_loop()
                roles = await loop.run_in_executor(None, casbin_enforcer.get_roles_for_user, result.username)
                if roles:
                    result._casbin_role = roles[0]
        except Exception:
            pass
        return result

    async def get_all_users(self) -> List[User]:
        """Get all users"""
        users, _ = await self.user_repo.get_multi()
        # attach casbin roles where present (run sync casbin calls in executor)
        try:
            loop = asyncio.get_event_loop()
            for u in users:
                roles = await loop.run_in_executor(None, casbin_enforcer.get_roles_for_user, u.username)
                if roles:
                    u._casbin_role = roles[0]
        except Exception:
            # enforcer may not be initialized yet; ignore
            pass
        return users

    async def create(self, obj_in: UserCreate) -> User:
        """Create a new user"""
        hashed = get_password_hash(obj_in.password)
        db_obj = obj_in.model_dump(exclude={"password"}, exclude_unset=True) if hasattr(obj_in, "model_dump") else obj_in.dict(exclude={"password"})
        db_obj["password_hash"] = hashed
        if "role" in db_obj:
            db_obj["user_role"] = db_obj.pop("role", None)
            
        # Don't commit - let endpoint handle commit after audit logging
        user = await self.user_repo.create(obj_in=db_obj, commit_txn=False)
        
        # Sync roles
        if user.user_role:
             stmt = select(Role).where(Role.name == user.user_role)
             result = await self.db.execute(stmt)
             role_obj = result.scalar_one_or_none()
             if role_obj:
                 # Use insert statement properly
                 insert_stmt = user_roles.insert().values(user_id=user.id, role_id=role_obj.id)
                 await self.db.execute(insert_stmt)
                 
                 # Sync to Casbin (run in threadpool since Casbin is synchronous)
                 loop = asyncio.get_event_loop()
                 await loop.run_in_executor(None, casbin_enforcer.sync_user_roles, user.username, [role_obj.name])
        
        # Flush to get ID and updated data but don't commit yet
        await self.db.flush()
        await self.db.refresh(user)
                 
        return user

    async def update(self, user_id: int, obj_in: Union[UserUpdate, dict]) -> Optional[User]:
        """Update a user"""
        try:
            # Get current user
            db_obj = await self.user_repo.get(user_id)
            if not db_obj:
                return None

            # Convert to dict if it's a Pydantic model
            update_data = obj_in if isinstance(obj_in, dict) else (obj_in.model_dump(exclude_unset=True) if hasattr(obj_in, "model_dump") else obj_in.dict(exclude_unset=True))

            # Normalize common aliases
            if "is_active" in update_data:
                update_data["active"] = update_data.pop("is_active")
            if "role" in update_data and "user_role" not in update_data:
                update_data["user_role"] = update_data.pop("role")

            # Filter out None values from update_data
            filtered_update_data = update_data

            # Handle password update separately
            if "password" in filtered_update_data and filtered_update_data["password"]:
                filtered_update_data["password_hash"] = get_password_hash(filtered_update_data["password"])
                del filtered_update_data["password"]  # remove plaintext password
            
            # Check if we need to sync roles
            role_changed = "user_role" in filtered_update_data
            
            # Don't commit - let the endpoint handle commit after audit logging
            updated_user = await self.user_repo.update(id=user_id, obj_in=filtered_update_data, commit_txn=False)
            
            # Sync roles if user_role was changed
            if role_changed:
                role_name = filtered_update_data["user_role"]
                stmt = select(Role).where(Role.name == role_name)
                result = await self.db.execute(stmt)
                role_obj = result.scalar_one_or_none()
                
                if role_obj:
                    # Clear existing roles and add new one in association table
                    delete_stmt = user_roles.delete().where(user_roles.c.user_id == user_id)
                    await self.db.execute(delete_stmt)
                    insert_stmt = user_roles.insert().values(user_id=user_id, role_id=role_obj.id)
                    await self.db.execute(insert_stmt)
                    
                    # Sync to Casbin (run in threadpool since Casbin is synchronous)
                    loop = asyncio.get_event_loop()
                    await loop.run_in_executor(None, casbin_enforcer.sync_user_roles, updated_user.username, [role_obj.name])
                
                # Flush to get updated values but don't commit yet
                await self.db.flush()
                await self.db.refresh(updated_user)

            return updated_user
        except IntegrityError as e:
            await self.db.rollback()
            error_msg = str(e.orig) if hasattr(e, 'orig') else str(e)
            if "unique constraint" in error_msg.lower():
                if "email" in error_msg.lower():
                    raise Exception("Email already in use")
                elif "username" in error_msg.lower():
                    raise Exception("Username already taken")
            raise Exception(f"Failed to update user: {error_msg}")
        except Exception as e:
            await self.db.rollback()
            raise

    async def delete(self, user_id: int) -> dict:
        """
        Delete a user (hard delete) with proper relationship formatting.
        Returns {"success": True/False, "error": str}
        """
        user = await self.user_repo.get(user_id)
        if not user:
            return {"success": False, "error": "User not found"}

        try:
            username = user.username
            
            # 1. Remove policies from Casbin (run in executor since Casbin is synchronous)
            if username:
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, casbin_enforcer.rbac_enforcer.remove_filtered_grouping_policy, 0, username)
                await loop.run_in_executor(None, casbin_enforcer.rbac_enforcer.save_policy)

            # 2. Nullify user references in audit logs so we can safely
            #    delete the user record while keeping the audit trail.
            #    We clear any FK columns that may point at this user.
            await self.db.execute(
                update(AuditLog).where(AuditLog.user_id == user_id).values(user_id=None)
            )
            await self.db.execute(
                update(AuditLog).where(AuditLog.created_by == user_id).values(created_by=None)
            )
            await self.db.execute(
                update(AuditLog).where(AuditLog.updated_by == user_id).values(updated_by=None)
            )
            await self.db.execute(
                update(AuditLog).where(AuditLog.deleted_by == user_id).values(deleted_by=None)
            )

            # 3. Remove User Roles (Association table cleanup)
            await self.db.execute(
                user_roles.delete().where(user_roles.c.user_id == user_id)
            )

            # 4. Attempt to delete generic relations if any (e.g., refresh tokens are cascade delete)
            # The repository delete call will cascade usually, but explicit cleanups help avoid 500s 
            
            # 5. Delete User - don't commit, let endpoint handle it after audit logging
            await self.user_repo.delete(id=user_id, commit_txn=False)
            
            return {"success": True}
            
        except IntegrityError as e:
            await self.db.rollback()
            # Check for common constraints
            err_msg = str(e).lower()
            if "form_submissions" in err_msg:
                return {"success": False, "error": "User cannot be deleted because they have form submissions. Deactivate them instead."}
            if "role" in err_msg:
                return {"success": False, "error": "User cannot be deleted due to role assignments."}
            return {"success": False, "error": f"Database integrity error: {str(e)}"}
            
        except Exception as e:
            await self.db.rollback()
            return {"success": False, "error": f"An unexpected error occurred: {str(e)}"}
   
    async def deactivate_user(self, user_id: int) -> Optional[User]:
        """
        Soft delete a user:
        - Set is_active = False
        - Remove roles from Casbin (access revocation)
        """
        user = await self.user_repo.get(user_id)
        if not user:
            return None
            
        # 1. Update active
        user.active = False
        self.db.add(user)
        
        # 2. Remove permissions/roles from Casbin
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, casbin_enforcer.rbac_enforcer.remove_filtered_grouping_policy, 0, user.username)
            await loop.run_in_executor(None, casbin_enforcer.rbac_enforcer.save_policy)
        except Exception as e:
            print(f"Error cleaning up Casbin for user {user.username}: {e}")
            
        # 3. Flush changes but don't commit - let endpoint handle commit after audit logging
        await self.db.flush()
        await self.db.refresh(user)
        
        return user