# API Examples: Database-Driven Permission System

## 🎯 Quick Start

### 1. Login and Get Token
```bash
curl -X POST "http://localhost:8000/api/v1/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -H "X-Client-ID: your-client-id" \
  -d "username=john.doe&password=password123"
```

**Response**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**JWT Payload** (decoded):
```json
{
  "user_id": 42,
  "sub": "john.doe",
  "user_role": "admin",
  "bank_id": 1,
  "permissions": [
    "policies:read",
    "policies:create",
    "policies:update",
    "policies:delete",
    "relationships:read",
    "relationships:create"
  ]
}
```

---

## 📋 ABAC API Examples

### List All Policies (Read)
**Permission Required**: `policies:read`

```bash
curl -X GET "http://localhost:8000/api/v1/abac/policies" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "X-Client-ID: your-client-id"
```

**Success Response (200 OK)**:
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "Department Access Policy",
      "description": "Users can only access resources in their department",
      "rules": {
        "conditions": [
          {
            "attribute": "user.department",
            "operator": "==",
            "value": "resource.department"
          }
        ],
        "action": "read"
      },
      "is_active": true,
      "created_at": "2026-01-28T10:00:00Z"
    }
  ]
}
```

**Error Response (403 Forbidden)** - User lacks permission:
```json
{
  "detail": "Missing required permission: policies:read"
}
```

### Create Policy (Create)
**Permission Required**: `policies:create`

```bash
curl -X POST "http://localhost:8000/api/v1/abac/policies" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "X-Client-ID: your-client-id" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Senior Level Access",
    "description": "Users with level >= 5 can access all resources",
    "rules": {
      "conditions": [
        {
          "attribute": "user.level",
          "operator": ">=",
          "value": 5
        }
      ],
      "action": "all"
    },
    "is_active": true
  }'
```

**Success Response (201 Created)**:
```json
{
  "success": true,
  "data": {
    "id": 2,
    "name": "Senior Level Access",
    "description": "Users with level >= 5 can access all resources",
    "rules": {
      "conditions": [
        {
          "attribute": "user.level",
          "operator": ">=",
          "value": 5
        }
      ],
      "action": "all"
    },
    "is_active": true,
    "created_at": "2026-01-30T14:23:45Z"
  }
}
```

### Update Policy (Update)
**Permission Required**: `policies:update`

```bash
curl -X PUT "http://localhost:8000/api/v1/abac/policies/2" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "X-Client-ID: your-client-id" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Senior Level Access",
    "description": "Users with level >= 3 can access resources",
    "rules": {
      "conditions": [
        {
          "attribute": "user.level",
          "operator": ">=",
          "value": 3
        }
      ],
      "action": "all"
    },
    "is_active": true
  }'
```

### Delete Policy (Delete)
**Permission Required**: `policies:delete`

```bash
curl -X DELETE "http://localhost:8000/api/v1/abac/policies/2" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "X-Client-ID: your-client-id"
```

**Success Response (204 No Content)**: Empty body

### Get Metadata (Any Policy Permission)
**Permission Required**: `policies:read` OR `policies:create` OR `policies:update`

```bash
curl -X GET "http://localhost:8000/api/v1/abac/metadata/attributes" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "X-Client-ID: your-client-id"
```

**Success Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "user_attributes": [
      {"key": "user.id", "label": "User ID", "type": "number"},
      {"key": "user.username", "label": "Username", "type": "string"},
      {"key": "user.department", "label": "Department", "type": "string"},
      {"key": "user.level", "label": "Level", "type": "number"}
    ],
    "resource_attributes": [
      {"key": "resource.id", "label": "Resource ID", "type": "string"},
      {"key": "resource.type", "label": "Resource Type", "type": "string"}
    ],
    "operators": [
      {"value": "==", "label": "Equals"},
      {"value": "!=", "label": "Not Equals"},
      {"value": ">", "label": "Greater Than"}
    ]
  }
}
```

---

## 🔗 ReBAC API Examples

### List All Relationships (Read)
**Permission Required**: `relationships:read`

```bash
curl -X GET "http://localhost:8000/api/v1/rebac/relationships" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "X-Client-ID: your-client-id"
```

**Success Response (200 OK)**:
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "subject_type": "user",
      "subject_id": "john.doe",
      "resource_type": "template",
      "resource_id": "template_123",
      "parent_resource_type": "bank",
      "parent_resource_id": "bank_1",
      "relationship_type": "owner",
      "created_at": "2026-01-28T10:00:00Z"
    }
  ]
}
```

### Create Relationship (Create)
**Permission Required**: `relationships:create`

```bash
curl -X POST "http://localhost:8000/api/v1/rebac/relationships" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "X-Client-ID: your-client-id" \
  -H "Content-Type: application/json" \
  -d '{
    "subject_type": "user",
    "subject_id": "jane.smith",
    "resource_type": "submission",
    "resource_id": "submission_456",
    "parent_resource_type": "template",
    "parent_resource_id": "template_123",
    "relationship_type": "viewer"
  }'
```

**Success Response (201 Created)**:
```json
{
  "success": true,
  "data": {
    "id": 2,
    "subject_type": "user",
    "subject_id": "jane.smith",
    "resource_type": "submission",
    "resource_id": "submission_456",
    "parent_resource_type": "template",
    "parent_resource_id": "template_123",
    "relationship_type": "viewer",
    "created_at": "2026-01-30T14:30:00Z"
  }
}
```

### Update Relationship (Update)
**Permission Required**: `relationships:update`

```bash
curl -X PUT "http://localhost:8000/api/v1/rebac/relationships/2" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "X-Client-ID: your-client-id" \
  -H "Content-Type: application/json" \
  -d '{
    "subject_type": "user",
    "subject_id": "jane.smith",
    "resource_type": "submission",
    "resource_id": "submission_456",
    "parent_resource_type": "template",
    "parent_resource_id": "template_123",
    "relationship_type": "editor"
  }'
```

### Delete Relationship (Delete)
**Permission Required**: `relationships:delete`

```bash
curl -X DELETE "http://localhost:8000/api/v1/rebac/relationships/2" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "X-Client-ID: your-client-id"
```

**Success Response (204 No Content)**: Empty body

### Get Metadata (Any Relationship Permission)
**Permission Required**: `relationships:read` OR `relationships:create` OR `relationships:update`

```bash
curl -X GET "http://localhost:8000/api/v1/rebac/metadata/options" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "X-Client-ID: your-client-id"
```

**Success Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "subject_types": ["user", "role", "group"],
    "resource_types": ["template", "submission", "bank", "document"],
    "relationship_types": ["owner", "viewer", "editor", "manager", "member"],
    "entities": {
      "users": [
        {"id": "1", "label": "john.doe"},
        {"id": "2", "label": "jane.smith"}
      ],
      "roles": [
        {"id": "1", "label": "admin"},
        {"id": "2", "label": "viewer"}
      ]
    }
  }
}
```

---

## 🔐 Permission Error Responses

### Missing Permission
```bash
# User tries to create policy without policies:create permission
curl -X POST "http://localhost:8000/api/v1/abac/policies" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "X-Client-ID: your-client-id" \
  -H "Content-Type: application/json" \
  -d '{"name": "Test", "description": "", "rules": {}, "is_active": true}'
```

**Response (403 Forbidden)**:
```json
{
  "detail": "Missing required permission: policies:create"
}
```

**Backend Log**:
```
❌ Permission denied: User 'john.doe' lacks 'policies:create'
   User has: ['forms:read', 'policies:read', 'templates:read']
```

### Inactive User
```bash
# User account is deactivated
curl -X GET "http://localhost:8000/api/v1/abac/policies" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "X-Client-ID: your-client-id"
```

**Response (403 Forbidden)**:
```json
{
  "detail": "Inactive user"
}
```

### Invalid Token
```bash
curl -X GET "http://localhost:8000/api/v1/abac/policies" \
  -H "Authorization: Bearer INVALID_TOKEN" \
  -H "X-Client-ID: your-client-id"
```

**Response (401 Unauthorized)**:
```json
{
  "detail": "Could not validate credentials"
}
```

---

## 🧪 Testing Permission Checks

### Test Script
```python
import requests

BASE_URL = "http://localhost:8000"
CLIENT_ID = "your-client-id"

# Login
login_response = requests.post(
    f"{BASE_URL}/api/v1/auth/token",
    headers={"X-Client-ID": CLIENT_ID},
    data={
        "username": "john.doe",
        "password": "password123"
    }
)

token = login_response.json()["access_token"]
headers = {
    "Authorization": f"Bearer {token}",
    "X-Client-ID": CLIENT_ID
}

# Test ABAC endpoints
print("Testing ABAC endpoints...")

# List policies
response = requests.get(f"{BASE_URL}/api/v1/abac/policies", headers=headers)
print(f"GET /abac/policies: {response.status_code}")

# Get metadata
response = requests.get(f"{BASE_URL}/api/v1/abac/metadata/attributes", headers=headers)
print(f"GET /abac/metadata/attributes: {response.status_code}")

# Test ReBAC endpoints
print("\nTesting ReBAC endpoints...")

# List relationships
response = requests.get(f"{BASE_URL}/api/v1/rebac/relationships", headers=headers)
print(f"GET /rebac/relationships: {response.status_code}")

# Get metadata
response = requests.get(f"{BASE_URL}/api/v1/rebac/metadata/options", headers=headers)
print(f"GET /rebac/metadata/options: {response.status_code}")
```

**Expected Output** (User with permissions):
```
Testing ABAC endpoints...
GET /abac/policies: 200
GET /abac/metadata/attributes: 200

Testing ReBAC endpoints...
GET /rebac/relationships: 200
GET /rebac/metadata/options: 200
```

**Expected Output** (User without permissions):
```
Testing ABAC endpoints...
GET /abac/policies: 403
GET /abac/metadata/attributes: 403

Testing ReBAC endpoints...
GET /rebac/relationships: 403
GET /rebac/metadata/options: 403
```

---

## 📊 Debugging Permission Issues

### Check User's Permissions
```bash
# Get current user info
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "X-Client-ID: your-client-id"
```

**Response**:
```json
{
  "id": 42,
  "username": "john.doe",
  "email": "john@example.com",
  "user_role": "viewer",
  "roles": [
    {
      "id": 2,
      "name": "viewer",
      "permissions": [
        "forms:read",
        "templates:read",
        "submissions:read"
      ]
    }
  ]
}
```

### Backend Logs
Enable debug logging to see permission checks:

```python
# backend/app/dependencies/permissions.py (already implemented)
print(f"✅ Permission granted: {current_user.username} has '{required_permission}'")
print(f"❌ Permission denied: User '{current_user.username}' lacks '{required_permission}'")
print(f"   User has: {sorted(user_permissions)}")
```

**Log Output**:
```
❌ Permission denied: User 'john.doe' lacks 'policies:create'
   User has: ['forms:read', 'submissions:read', 'templates:read']
```

---

## 🎓 Common Scenarios

### Scenario 1: Policy Viewer (Read-Only)
**Role**: `policy_viewer`
**Permissions**: `["policies:read"]`

**Can Do**:
- ✅ List all policies
- ✅ View specific policy
- ✅ Get metadata (for understanding structure)

**Cannot Do**:
- ❌ Create new policies
- ❌ Update existing policies
- ❌ Delete policies

### Scenario 2: Policy Manager (Full Access)
**Role**: `policy_manager`
**Permissions**: `["policies:create", "policies:read", "policies:update", "policies:delete"]`

**Can Do**:
- ✅ Create new policies
- ✅ List all policies
- ✅ View specific policy
- ✅ Update policies
- ✅ Delete policies
- ✅ Get metadata

### Scenario 3: Relationship Admin (ReBAC Only)
**Role**: `relationship_admin`
**Permissions**: `["relationships:create", "relationships:read", "relationships:update", "relationships:delete"]`

**Can Do**:
- ✅ Manage all ReBAC relationships
- ✅ Get ReBAC metadata

**Cannot Do**:
- ❌ Access ABAC endpoints (no policies:* permissions)

### Scenario 4: Dual Admin (ABAC + ReBAC)
**Role**: `admin`
**Permissions**: `["policies:*", "relationships:*", ...]`

**Can Do**:
- ✅ Full access to ABAC endpoints
- ✅ Full access to ReBAC endpoints
- ✅ All other system features

---

## 🔧 Troubleshooting

### Problem: 403 Forbidden despite having permission in UI

**Check**:
1. Verify permission is in database:
   ```sql
   SELECT r.name, r.permissions
   FROM roles r
   WHERE r.id IN (SELECT role_id FROM user_roles WHERE user_id = 42);
   ```

2. Check user-role assignment:
   ```sql
   SELECT u.username, r.name
   FROM users u
   JOIN user_roles ur ON u.id = ur.user_id
   JOIN roles r ON ur.role_id = r.id
   WHERE u.username = 'john.doe';
   ```

3. Verify JWT has permissions:
   - Decode token at [jwt.io](https://jwt.io)
   - Check `permissions` array
   - If missing, logout and login again to refresh token

### Problem: Metadata endpoint returns 403

**Cause**: User has no permissions in that domain

**Solution**: Grant at least one permission:
- For ABAC metadata: Need `policies:read`, `policies:create`, or `policies:update`
- For ReBAC metadata: Need `relationships:read`, `relationships:create`, or `relationships:update`

### Problem: Server shows "Enforcer not initialized"

**Cause**: Casbin initialization failed

**Solution**: Check database connection and Casbin tables exist

---

## ✅ Success Checklist

- [ ] User can login and get JWT token
- [ ] JWT contains permissions array
- [ ] User with `policies:read` can access `/abac/policies`
- [ ] User with `relationships:read` can access `/rebac/relationships`
- [ ] User without permission gets 403 error
- [ ] Metadata endpoints work with any related permission
- [ ] Frontend sidebar shows/hides based on permissions
- [ ] Backend logs show clear permission check results
