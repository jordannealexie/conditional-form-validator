# Permission Fix Summary

## Problem Description
Non-admin users (supervisor, fieldman roles) could not access or submit templates even when they had all permissions checked in their roles.

## Root Cause
The issue was caused by missing user-to-role mappings in Casbin. When permissions were added to roles through the admin interface:
1. The permissions were stored in the database (`roles` table)
2. The permissions were synced to Casbin policies
3. **BUT** users were not re-synced with their roles in Casbin

This meant Casbin didn't know which users belonged to which roles, so even though the roles had permissions, users couldn't use them.

## Solution Implemented

### 1. **Login Time Role Sync** 
Modified [auth.py](../app/api/v1/endpoints/auth.py) to sync user roles to Casbin on every login. This ensures:
- Fresh role mappings even if permissions change after user creation
- Users get the latest permissions for their role
- No need for manual intervention

### 2. **Enhanced Permission Debugging**
Added comprehensive debugging to [casbin_enforcer.py](../app/core/casbin_enforcer.py):
- Shows which roles a user has
- Shows which permissions each role has
- Shows the result of permission checks
- Helps identify permission issues quickly

### 3. **Permission Sync Scripts**

Created utility scripts to manage permissions:

#### `scripts/ensure_permissions.py`
- Sets default permissions for all roles (admin, supervisor, fieldman)
- Updates both database and Casbin
- Can be run anytime to reset permissions to defaults

#### `scripts/sync_user_roles.py`
- Syncs all existing users' roles to Casbin
- Verifies the sync by sampling users
- Shows which users were synced

#### `scripts/fix_permissions.sh`
- Master script that runs both ensure_permissions and sync_user_roles
- One command to fix all permission issues
- Usage: `bash scripts/fix_permissions.sh`

#### `scripts/verify_policies.py`
- Verifies Casbin policies are correctly set
- Shows permissions for each role
- Tests sample users
- Runs test cases to verify permissions work

## Default Permissions by Role

### Admin
- Full access to all resources
- users: create, read, update, delete
- templates/forms: create, read, update, delete
- submissions: create, read, update, delete, review
- roles: create, read, update, delete

### Supervisor
- users: read
- templates/forms: read
- submissions: read, review

### Fieldman
- templates/forms: read
- submissions: create, read, update, delete

## How to Fix Permission Issues

### If users can't access features:

1. **Run the fix script:**
   ```bash
   cd backend
   bash scripts/fix_permissions.sh
   ```

2. **Ask affected users to log out and log in again**
   - This triggers the role sync at login time
   - Users will get fresh permissions

### If you modify role permissions in the admin panel:

Users will automatically get the new permissions on their next login. No manual intervention needed.

### To verify permissions are working:

```bash
cd backend
source venv/bin/activate
python3 scripts/verify_policies.py
```

## Files Modified

1. [app/api/v1/endpoints/auth.py](../app/api/v1/endpoints/auth.py)
   - Added role sync on login
   - Enhanced permission retrieval to include role permissions

2. [app/core/casbin_enforcer.py](../app/core/casbin_enforcer.py)
   - Added detailed debugging output
   - Enhanced error handling
   - Fixed attribute access issues

3. [scripts/ensure_permissions.py](../scripts/ensure_permissions.py)
   - Updated to handle both "fieldman" and "user" roles

4. New scripts created:
   - [scripts/sync_user_roles.py](../scripts/sync_user_roles.py)
   - [scripts/fix_permissions.sh](../scripts/fix_permissions.sh)
   - [scripts/verify_policies.py](../scripts/verify_policies.py)

## Technical Details

### Casbin RBAC Model
The system uses Casbin's RBAC (Role-Based Access Control) model with:
- **Grouping policies (g)**: Map users to roles (e.g., `fieldman1 -> fieldman`)
- **Permission policies (p)**: Map roles to resource permissions (e.g., `fieldman -> submissions -> create`)

The matcher checks: `g(r.sub, p.sub) && r.obj == p.obj && r.act == p.act`
This means: "Does the user have a role that has permission for this resource and action?"

### Why the Fix Works
1. **Login Sync**: Ensures user-role mappings are always fresh
2. **Permission Sync**: Ensures role-permission mappings are correct
3. **Debugging**: Makes it easy to identify issues

## Testing

All test cases passed in verification:
- ✅ fieldman1 can create/read submissions
- ✅ fieldman1 can read forms/templates
- ✅ fieldman1 cannot create users (correctly denied)
- ✅ supervisors can read and review submissions
- ✅ supervisors cannot create submissions (correctly denied)
- ✅ admin has full access

## Notes

- The fix is **backward compatible** - existing functionality is preserved
- **No database schema changes** required
- **No frontend changes** required
- Users just need to **log out and log in** to get the fix
- The server restart will also pick up the new role sync logic
