# Database-Driven Permission System

## ✅ Problem Solved

Users with permissions assigned via the **Roles & Permissions UI** were receiving 403 Forbidden errors because:

1. **Old system**: Checked `is_superuser` flag OR Casbin policies (2 separate layers)
2. **Database permissions**: Stored in `roles.permissions` JSON column (from UI checkboxes)
3. **Casbin policies**: Separate, manually managed, not synced with database

**The gap**: Backend used Casbin, but permissions were only set in the database via UI.

---

## 🔧 New Architecture

### Permission Flow

```
┌─────────────────────────────────────────────────────┐
│  Frontend: Roles & Permissions UI                   │
│  (Admin assigns checkboxes like policies:read)      │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│  Database: roles.permissions (JSON column)          │
│  ["policies:read", "policies:create", ...]          │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│  User → Roles → Permissions (many-to-many)          │
│  Via user_roles junction table                      │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│  FastAPI Dependency: require_permission()           │
│  Queries database on EVERY request                  │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│  Endpoint: GET /api/v1/abac/policies                │
│  ✅ Access granted if user has policies:read        │
└─────────────────────────────────────────────────────┘
```

---

## 📁 Database Schema

### Roles Table
```sql
CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR UNIQUE NOT NULL,
    description VARCHAR,
    permissions JSONB,  -- ["policies:read", "relationships:create", ...]
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

### User-Role Association
```sql
CREATE TABLE user_roles (
    user_id INTEGER REFERENCES users(id),
    role_id INTEGER REFERENCES roles(id),
    PRIMARY KEY (user_id, role_id)
);
```

### Example Data
```sql
-- Role with ABAC/ReBAC permissions
INSERT INTO roles (name, permissions) VALUES (
    'Policy Manager',
    '["policies:read", "policies:create", "policies:update", "policies:delete"]'::jsonb
);

-- Assign role to user
INSERT INTO user_roles (user_id, role_id)
VALUES (5, 2);  -- User ID 5 gets Policy Manager role
```

---

## 🔑 Permission Format

All permissions follow the pattern: `resource:action`

### ABAC Permissions
```json
[
  "policies:create",
  "policies:read",
  "policies:update",
  "policies:delete"
]
```

### ReBAC Permissions
```json
[
  "relationships:create",
  "relationships:read",
  "relationships:update",
  "relationships:delete"
]
```

### Other Resources
```json
[
  "users:read",
  "templates:create",
  "submissions:review",
  "forms:delete",
  "roles:update"
]
```

---

## 🛠️ Implementation

### 1. Permission Checker Function

**Location**: `backend/app/dependencies/permissions.py`

```python
async def get_user_permissions_from_db(user: User, db: AsyncSession) -> Set[str]:
    """
    Fetch all permissions for a user from database role assignments.
    
    Steps:
    1. Query user with eagerly loaded roles
    2. Extract permissions JSON from each role
    3. Return union of all permissions
    
    Returns:
        Set of permission strings like {"policies:read", "relationships:write"}
    """
    stmt = select(User).where(User.id == user.id).options(selectinload(User.roles))
    result = await db.execute(stmt)
    user_with_roles = result.scalar_one_or_none()
    
    if not user_with_roles:
        return set()
    
    all_permissions = set()
    for role in user_with_roles.roles:
        if role.permissions and isinstance(role.permissions, list):
            all_permissions.update(role.permissions)
    
    return all_permissions
```

### 2. Reusable Permission Dependencies

#### Single Permission Check
```python
def require_permission(required_permission: str):
    """
    Checks if user has a specific permission.
    
    Usage:
        @router.get("/abac/policies")
        async def list_policies(
            user: User = Depends(require_permission("policies:read"))
        ):
            ...
    """
    async def check_permission(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
    ) -> User:
        if not current_user.active:
            raise HTTPException(status_code=403, detail="Inactive user")
        
        user_permissions = await get_user_permissions_from_db(current_user, db)
        
        if required_permission not in user_permissions:
            raise HTTPException(
                status_code=403,
                detail=f"Missing required permission: {required_permission}"
            )
        
        return current_user
    
    return check_permission
```

#### Any Permission Check (OR Logic)
```python
def require_any_permission(*required_permissions: str):
    """
    Checks if user has ANY of the listed permissions.
    
    Usage:
        @router.get("/abac/metadata")
        async def get_metadata(
            user: User = Depends(require_any_permission(
                "policies:read",
                "policies:create",
                "policies:update"
            ))
        ):
            ...
    """
    async def check_permission(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
    ) -> User:
        if not current_user.active:
            raise HTTPException(status_code=403, detail="Inactive user")
        
        user_permissions = await get_user_permissions_from_db(current_user, db)
        has_permission = any(perm in user_permissions for perm in required_permissions)
        
        if not has_permission:
            raise HTTPException(
                status_code=403,
                detail=f"Need one of: {', '.join(required_permissions)}"
            )
        
        return current_user
    
    return check_permission
```

---

## 📝 Endpoint Examples

### ABAC Endpoints

**Before (hardcoded superuser check)**:
```python
@router.get("/policies")
async def list_abac_policies(
    current_user: User = Depends(require_superuser)  # ❌ Only superusers
):
    ...
```

**After (database permission check)**:
```python
@router.get("/policies")
async def list_abac_policies(
    current_user: User = Depends(require_permission("policies:read"))  # ✅ DB-driven
):
    """List all ABAC policies - requires policies:read permission"""
    ...
```

### Full ABAC Endpoint Set
```python
# POST /abac/policies - Create policy
@router.post("/policies")
async def create_abac_policy(
    user: User = Depends(require_permission("policies:create"))
):
    ...

# GET /abac/policies - List policies
@router.get("/policies")
async def list_abac_policies(
    user: User = Depends(require_permission("policies:read"))
):
    ...

# PUT /abac/policies/{id} - Update policy
@router.put("/policies/{policy_id}")
async def update_abac_policy(
    user: User = Depends(require_permission("policies:update"))
):
    ...

# DELETE /abac/policies/{id} - Delete policy
@router.delete("/policies/{policy_id}")
async def delete_abac_policy(
    user: User = Depends(require_permission("policies:delete"))
):
    ...

# GET /abac/metadata/attributes - Get metadata (read-only)
@router.get("/metadata/attributes")
async def get_available_attributes(
    user: User = Depends(require_any_permission(
        "policies:read",
        "policies:create",
        "policies:update"
    ))
):
    """
    Metadata endpoints allow access to users with ANY policy permission.
    Rationale: Users creating/updating policies need metadata to build rules.
    """
    ...
```

### ReBAC Endpoints

```python
# POST /rebac/relationships - Create relationship
@router.post("/relationships")
async def create_relationship(
    user: User = Depends(require_permission("relationships:create"))
):
    ...

# GET /rebac/relationships - List relationships
@router.get("/relationships")
async def list_relationships(
    user: User = Depends(require_permission("relationships:read"))
):
    ...

# PUT /rebac/relationships/{id} - Update relationship
@router.put("/relationships/{relationship_id}")
async def update_relationship(
    user: User = Depends(require_permission("relationships:update"))
):
    ...

# DELETE /rebac/relationships/{id} - Delete relationship
@router.delete("/relationships/{relationship_id}")
async def delete_relationship(
    user: User = Depends(require_permission("relationships:delete"))
):
    ...

# GET /rebac/metadata/options - Get metadata
@router.get("/metadata/options")
async def get_rebac_options(
    user: User = Depends(require_any_permission(
        "relationships:read",
        "relationships:create",
        "relationships:update"
    ))
):
    """Metadata for relationship creation - needs any relationship permission"""
    ...
```

---

## 🔄 Metadata Endpoint Strategy

### What Are Metadata Endpoints?

Metadata endpoints return **reference data** needed to build forms/UI:
- Available attributes for ABAC policy conditions
- Available relationship types for ReBAC
- Entity lists (users, roles, templates) for dropdowns

### Permission Strategy

**Use `require_any_permission()`** for metadata endpoints because:

1. **Read-only data**: Metadata doesn't modify policies/relationships
2. **UI dependency**: Users creating/updating resources NEED metadata
3. **Better UX**: Don't force users to have separate "read" permission just to create

**Example**:
```python
@router.get("/metadata/attributes")
async def get_metadata(
    user: User = Depends(require_any_permission(
        "policies:read",     # Can list existing policies
        "policies:create",   # Can create new policies (needs metadata)
        "policies:update"    # Can update policies (needs metadata)
    ))
):
    # Returns: list of available attributes, operators, field types
    ...
```

### Why Not Public?

Even though metadata is reference data, it reveals system structure:
- User attribute names
- Available roles
- Resource types

So it still requires **some** permission in that domain.

---

## 🎯 Frontend Integration

### Sidebar Visibility

**Frontend checks same permissions**:

```javascript
// frontend/js/api.js
async function getUserPermissions() {
    const token = localStorage.getItem('token');
    const response = await fetch('/api/v1/auth/me', {
        headers: { 'Authorization': `Bearer ${token}` }
    });
    const data = await response.json();
    return data.permissions; // Array from JWT
}

// Show/hide ABAC menu
const permissions = await getUserPermissions();
if (permissions.includes('policies:read') || 
    permissions.includes('policies:create')) {
    document.querySelector('#abac-menu').style.display = 'block';
}
```

### Permission Source of Truth

**Both frontend and backend use the same source**:

```
JWT Token Payload
{
  "user_id": 42,
  "sub": "john.doe",
  "permissions": [
    "policies:read",
    "policies:create",
    "relationships:read"
  ]
}
```

Permissions are embedded in JWT during login:

```python
# backend/app/api/v1/endpoints/auth.py
@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm):
    # Authenticate user
    user = await authenticate_user(username, password)
    
    # Get permissions from database
    user_permissions = await get_user_permissions_from_db(user, db)
    
    # Create token with permissions
    token_data = {
        "user_id": user.id,
        "sub": user.username,
        "permissions": list(user_permissions)  # Embedded in JWT
    }
    
    access_token = create_access_token(data=token_data)
    return {"access_token": access_token, "token_type": "bearer"}
```

---

## 📊 SQL Queries to Check Permissions

### Get all permissions for a user
```sql
SELECT DISTINCT
    jsonb_array_elements_text(r.permissions) AS permission
FROM users u
JOIN user_roles ur ON u.id = ur.user_id
JOIN roles r ON ur.role_id = r.id
WHERE u.username = 'john.doe';
```

### Find users with specific permission
```sql
SELECT DISTINCT u.username, u.email
FROM users u
JOIN user_roles ur ON u.id = ur.user_id
JOIN roles r ON ur.role_id = r.id
WHERE r.permissions @> '["policies:read"]'::jsonb;
```

### Check if user has permission
```sql
SELECT EXISTS (
    SELECT 1
    FROM users u
    JOIN user_roles ur ON u.id = ur.user_id
    JOIN roles r ON ur.role_id = r.id
    WHERE u.username = 'john.doe'
      AND r.permissions @> '["policies:create"]'::jsonb
) AS has_permission;
```

### Update role permissions
```sql
UPDATE roles
SET permissions = '["policies:read", "policies:create", "policies:update"]'::jsonb
WHERE name = 'Policy Manager';
```

---

## 🧪 Testing

### Test Permission Check
```python
import asyncio
from app.db.session import AsyncSessionLocal
from app.dependencies.permissions import get_user_permissions_from_db
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.user import User

async def test_permissions():
    async with AsyncSessionLocal() as db:
        # Get user
        result = await db.execute(
            select(User)
            .where(User.username == "john.doe")
            .options(selectinload(User.roles))
        )
        user = result.scalar_one()
        
        # Get permissions
        permissions = await get_user_permissions_from_db(user, db)
        print(f"User {user.username} has permissions: {permissions}")
        
        # Check specific permission
        has_policies_read = "policies:read" in permissions
        print(f"Has policies:read? {has_policies_read}")

asyncio.run(test_permissions())
```

### Test API Endpoint
```bash
# Login to get token
TOKEN=$(curl -X POST "http://localhost:8000/api/v1/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=john.doe&password=password123" \
  | jq -r '.access_token')

# Test ABAC endpoint
curl -X GET "http://localhost:8000/api/v1/abac/policies" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Client-ID: your-client-id"

# Expected responses:
# ✅ 200 OK - User has policies:read permission
# ❌ 403 Forbidden - User lacks policies:read permission
```

---

## ✨ Key Advantages

### 1. **Single Source of Truth**
- ✅ Permissions defined ONCE in database
- ✅ No Casbin sync required
- ✅ UI checkboxes = actual permissions

### 2. **Dynamic & Scalable**
- ✅ No code changes to add new permissions
- ✅ Admin can modify via UI
- ✅ Changes take effect immediately

### 3. **No Hardcoded Logic**
- ❌ No `if user.is_superuser` checks
- ❌ No hardcoded role names
- ✅ Pure permission-based access control

### 4. **Granular Control**
- ✅ Separate create/read/update/delete permissions
- ✅ Different roles can have different permission sets
- ✅ Users can have multiple roles

### 5. **Auditable**
- ✅ All permissions stored in database
- ✅ Can query who has what permission
- ✅ Easy to generate compliance reports

---

## 🚨 Important Notes

### Superuser Bypass (Optional)

The new system does NOT check `is_superuser` by default. To re-enable:

```python
def require_permission(required_permission: str):
    async def check_permission(current_user: User, db: AsyncSession) -> User:
        # Add this line to allow superuser bypass
        if current_user.is_superuser:
            return current_user
        
        # Continue with permission check
        user_permissions = await get_user_permissions_from_db(current_user, db)
        ...
```

**Recommendation**: Don't use superuser bypass. Assign permissions explicitly.

### JWT Token Size

Embedding permissions in JWT increases token size. For users with many roles:
- Typical: 20-30 permissions = ~500 bytes
- Large: 100+ permissions = may exceed browser limits

**Solution**: Only embed permission count in JWT, fetch from DB on each request (current implementation).

### Caching Considerations

Current implementation queries database on **every request**. For high-traffic apps:

```python
from functools import lru_cache
from datetime import datetime, timedelta

# Cache permissions for 5 minutes
@lru_cache(maxsize=1000)
async def get_user_permissions_cached(user_id: int, cache_key: str):
    async with AsyncSessionLocal() as db:
        return await get_user_permissions_from_db(user, db)

# Usage with TTL
def require_permission(perm: str):
    async def check(user: User, db: AsyncSession):
        cache_key = f"{datetime.utcnow().timestamp() // 300}"  # 5-min buckets
        permissions = await get_user_permissions_cached(user.id, cache_key)
        ...
```

---

## 📚 Related Files

- **Permission Logic**: `backend/app/dependencies/permissions.py`
- **ABAC Endpoints**: `backend/app/api/v1/endpoints/abac.py`
- **ReBAC Endpoints**: `backend/app/api/v1/endpoints/rebac.py`
- **User Model**: `backend/app/models/user.py`
- **Role Schema**: Database table `roles` with JSONB `permissions` column

---

## 🎓 Summary

This system provides:
- ✅ **No hardcoded permissions**
- ✅ **Database-driven authorization**
- ✅ **Dynamic role management via UI**
- ✅ **Reusable permission dependencies**
- ✅ **Consistent frontend/backend permission checks**
- ✅ **Granular resource:action permissions**
- ✅ **Metadata endpoints with logical access rules**

**Result**: Users with permissions assigned via Roles & Permissions UI can now access ABAC and ReBAC pages without 403 errors.
