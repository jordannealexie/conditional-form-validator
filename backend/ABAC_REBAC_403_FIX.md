# ABAC/ReBAC 403 Forbidden Fix

## Problem Summary

Users with assigned ABAC/ReBAC permissions were getting 403 Forbidden errors:
- `GET /api/v1/abac/metadata/attributes` → 403 Forbidden
- `GET /api/v1/abac/policies` → 403 Forbidden  
- `GET /api/v1/rebac/metadata/options` → 403 Forbidden
- `GET /api/v1/rebac/relationships` → 403 Forbidden

**Error message:** "Superuser privileges required"

## Root Cause

All ABAC/ReBAC endpoints were using the `require_superuser` dependency, which had a **hardcoded check** that only allowed `is_superuser=True` users. This completely bypassed the permission system.

### Before (Broken Code)

```python
# permissions.py - Line 154
def require_superuser(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Superuser privileges required"  # ❌ Hard fail
        )
    return current_user

# abac.py - Line 44
@router.get("/policies")
async def list_abac_policies(
    current_user: User = Depends(require_superuser)  # ❌ Only superusers allowed
):
```

**Why this is wrong:**
- Ignores all RBAC/ABAC/ReBAC policies assigned to users
- Makes permission assignments in the database useless
- Forces you to make users superusers (security anti-pattern)

## The Fix

### 1. Created New Flexible Dependency

Added `require_admin_or_permission()` in `app/dependencies/permissions.py`:

```python
def require_admin_or_permission(resource: str, action: str):
    """
    Allows both superusers AND users with explicit permissions.
    """
    async def check_permission(current_user: User = Depends(get_current_user)) -> User:
        if not current_user.is_active:
            raise HTTPException(status_code=403, detail="Inactive user")
        
        # ✅ Superuser bypass (backward compatibility)
        if current_user.is_superuser:
            return current_user
        
        # ✅ Check Casbin RBAC permission
        has_permission = await casbin_enforcer.check_rbac_permission_async(
            current_user.username,
            resource,
            action
        )
        
        if not has_permission:
            raise HTTPException(
                status_code=403,
                detail=f"Insufficient permissions: requires superuser or explicit permission to {action} {resource}"
            )
        
        return current_user
    
    return check_permission
```

### 2. Updated All ABAC/ReBAC Endpoints

**ABAC Endpoints** (`app/api/v1/endpoints/abac.py`):
```python
# Before:
@router.get("/policies")
async def list_abac_policies(
    current_user: User = Depends(require_superuser)  # ❌
):

# After:
@router.get("/policies")
async def list_abac_policies(
    current_user: User = Depends(require_admin_or_permission("abac", "read"))  # ✅
):
```

**ReBAC Endpoints** (`app/api/v1/endpoints/rebac.py`):
```python
# Before:
@router.get("/relationships")
async def list_relationships(
    current_user: User = Depends(require_superuser)  # ❌
):

# After:
@router.get("/relationships")
async def list_relationships(
    current_user: User = Depends(require_admin_or_permission("rebac", "read"))  # ✅
):
```

### 3. Permission Mapping

| Endpoint | Resource | Action | Who Can Access |
|----------|----------|--------|----------------|
| GET /abac/policies | `abac` | `read` | Superusers OR users with `abac:read` permission |
| POST /abac/policies | `abac` | `write` | Superusers OR users with `abac:write` permission |
| DELETE /abac/policies/{id} | `abac` | `delete` | Superusers OR users with `abac:delete` permission |
| GET /rebac/relationships | `rebac` | `read` | Superusers OR users with `rebac:read` permission |
| POST /rebac/relationships | `rebac` | `write` | Superusers OR users with `rebac:write` permission |

## How to Grant Permissions

### Option 1: Using the Script (Recommended)

```bash
cd /home/vboxuser/conditional-form-validator-backend/backend

# Verify current user permissions
python scripts/grant_abac_rebac_access.py verify your_username

# Grant all ABAC/ReBAC permissions to a user
python scripts/grant_abac_rebac_access.py grant-user your_username

# Grant to a role (then assign users to the role)
python scripts/grant_abac_rebac_access.py grant-role abac_admin
python scripts/grant_abac_rebac_access.py assign your_username abac_admin

# List all current ABAC/ReBAC permissions
python scripts/grant_abac_rebac_access.py list
```

### Option 2: Direct SQL

```sql
-- Grant ABAC permissions to a user
INSERT INTO casbin_rule (ptype, v0, v1, v2) 
VALUES 
    ('p', 'your_username', 'abac', 'read'),
    ('p', 'your_username', 'abac', 'write'),
    ('p', 'your_username', 'abac', 'delete')
ON CONFLICT DO NOTHING;

-- Grant ReBAC permissions to a user
INSERT INTO casbin_rule (ptype, v0, v1, v2) 
VALUES 
    ('p', 'your_username', 'rebac', 'read'),
    ('p', 'your_username', 'rebac', 'write'),
    ('p', 'your_username', 'rebac', 'delete')
ON CONFLICT DO NOTHING;

-- Reload Casbin policies (restart app or call reload endpoint)
```

### Option 3: Python Code

```python
from app.core.casbin_enforcer import casbin_enforcer

# Grant ABAC read permission
await casbin_enforcer.add_policy_async("username", "abac", "read")
await casbin_enforcer.add_policy_async("username", "abac", "write")

# Grant ReBAC permissions
await casbin_enforcer.add_policy_async("username", "rebac", "read")
await casbin_enforcer.add_policy_async("username", "rebac", "write")
```

## Frontend Alignment

The frontend sidebar visibility should now match backend permissions:

```javascript
// frontend/js/auth.js or similar
async function checkABACAccess() {
    try {
        const response = await fetch('/api/v1/abac/policies', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        return response.ok; // 200 = has access, 403 = no access
    } catch {
        return false;
    }
}

// Only show ABAC menu if user has access
if (await checkABACAccess()) {
    showABACMenuItem();
}
```

Or check permissions proactively:
```javascript
// Store user permissions on login
const userPermissions = await fetchUserPermissions(); // Returns ['abac:read', 'rebac:write', ...]

// Show/hide menu items based on permissions
if (userPermissions.includes('abac:read')) {
    showABACMenuItem();
}
if (userPermissions.includes('rebac:read')) {
    showReBACMenuItem();
}
```

## Testing the Fix

1. **Create a test user without superuser privileges:**
   ```sql
   INSERT INTO users (username, email, user_role, is_superuser) 
   VALUES ('test_user', 'test@example.com', 'user', false);
   ```

2. **Grant ABAC/ReBAC permissions:**
   ```bash
   python scripts/grant_abac_rebac_access.py grant-user test_user
   ```

3. **Login as test_user and verify:**
   - ✅ Can access `/abac` page
   - ✅ Can see ABAC policies
   - ✅ Can access `/rebac` page
   - ✅ Can see ReBAC relationships
   - ❌ Cannot access other admin endpoints (users, roles) without those permissions

4. **Check logs:**
   ```bash
   # Should NOT see "Superuser privileges required"
   # Should see successful requests with 200 status
   ```

## Key Architectural Lessons

### ❌ Anti-Pattern: Hardcoded Role Checks
```python
# DON'T DO THIS
if not user.is_superuser:
    raise HTTPException(403, "Admin only")
```
**Why bad:** Bypasses your entire permission system

### ✅ Best Practice: Permission-Based Authorization
```python
# DO THIS
if not user.is_superuser:
    has_perm = await check_permission(user, resource, action)
    if not has_perm:
        raise HTTPException(403, "Insufficient permissions")
```
**Why good:** 
- Respects permission system
- Allows granular access control
- Superusers still have full access
- Easy to audit and modify

### Authorization Layer Structure

```
Frontend Request
    ↓
JWT Validation (authenticate)
    ↓
Permission Check Dependency (authorize)
    ├─ Is superuser? → ✅ Allow
    ├─ Has explicit permission? → ✅ Allow
    └─ Neither? → ❌ 403 Forbidden
    ↓
Endpoint Handler (business logic)
```

## Files Modified

1. **`app/dependencies/permissions.py`**
   - Added `require_admin_or_permission()` dependency factory

2. **`app/api/v1/endpoints/abac.py`**
   - Replaced all `require_superuser` with `require_admin_or_permission("abac", <action>)`
   - Affected endpoints: policies, attributes, metadata

3. **`app/api/v1/endpoints/rebac.py`**
   - Replaced all `require_superuser` with `require_admin_or_permission("rebac", <action>)`
   - Affected endpoints: relationships, metadata

4. **`scripts/grant_abac_rebac_access.py`** (New)
   - CLI tool to manage ABAC/ReBAC permissions

5. **`scripts/grant_abac_rebac_permissions.sql`** (New)
   - SQL script for direct database permission grants

## Summary

**Problem:** Hardcoded superuser checks blocked all non-superusers from ABAC/ReBAC pages.

**Solution:** Replaced `require_superuser` with flexible `require_admin_or_permission()` that checks:
1. Is user a superuser? → Allow
2. Does user have explicit permission? → Allow  
3. Neither? → Deny

**Result:** 
- ✅ Superusers retain full access
- ✅ Non-superusers with permissions can access ABAC/ReBAC
- ✅ Permission system is actually used
- ✅ Security is maintained (still requires explicit grants)
