# Permission System Quick Reference

## Problem Solved ✅

Non-admin users (supervisor, fieldman) can now access templates and submit forms after you checked all their permissions.

## Quick Actions

### For Users Having Permission Issues

**Ask them to log out and log in again.** That's it!

The new login process automatically syncs their roles and permissions.

### Check If a User Has Access

```bash
cd backend
source venv/bin/activate
python3 scripts/check_user_access.py <username> <resource> <action>
```

Example:
```bash
python3 scripts/check_user_access.py fieldman1 submissions create
# Output: ✅ GRANTED - User can create submissions
```

### Reset All Permissions to Defaults

```bash
cd backend
bash scripts/fix_permissions.sh
```

This will:
- Set default permissions for admin, supervisor, fieldman roles
- Sync all users with their roles
- Verify the setup

### Test All Permissions

```bash
cd backend
source venv/bin/activate
python3 scripts/test_permissions.py
```

Shows comprehensive test results for supervisors and fieldmen.

### Verify Casbin Policies

```bash
cd backend
source venv/bin/activate
python3 scripts/verify_policies.py
```

Shows:
- What permissions each role has
- Which roles each user has
- Test cases verifying permissions work

## Default Permissions by Role

### Admin (Full Access)
- ✅ users: create, read, update, delete
- ✅ templates/forms: create, read, update, delete
- ✅ submissions: create, read, update, delete, review
- ✅ roles: create, read, update, delete

### Supervisor (Read + Review)
- ✅ users: read
- ✅ templates/forms: read
- ✅ submissions: read, review
- ❌ Cannot create/edit anything

### Fieldman (Submit Forms)
- ✅ templates/forms: read
- ✅ submissions: create, read, update, delete
- ❌ Cannot review submissions
- ❌ Cannot access users

## Utility Scripts

All scripts are in `backend/scripts/`:

| Script | Purpose | Usage |
|--------|---------|-------|
| `fix_permissions.sh` | Fix all permission issues | `bash scripts/fix_permissions.sh` |
| `check_user_access.py` | Check specific user access | `python3 scripts/check_user_access.py user resource action` |
| `test_permissions.py` | Run comprehensive tests | `python3 scripts/test_permissions.py` |
| `verify_policies.py` | Verify Casbin setup | `python3 scripts/verify_policies.py` |
| `sync_user_roles.py` | Sync all user roles | `python3 scripts/sync_user_roles.py` |
| `ensure_permissions.py` | Set default permissions | `python3 scripts/ensure_permissions.py` |

## How It Works Now

### Before (Broken):
1. Admin checks permissions for a role ✓
2. Permissions saved to database ✓
3. Permissions synced to Casbin ✓
4. **User-role mapping NOT in Casbin** ✗
5. User can't access anything ❌

### After (Fixed):
1. Admin checks permissions for a role ✓
2. Permissions saved to database ✓
3. Permissions synced to Casbin ✓
4. User logs in → **Role automatically synced** ✓
5. User can access everything allowed by their role ✅

## Troubleshooting

### Users still can't access after logging out/in

1. Check if user has correct role:
   ```bash
   python3 scripts/check_user_access.py <username> <resource> <action>
   ```

2. Verify role has permissions:
   ```bash
   python3 scripts/verify_policies.py
   ```

3. Run fix script:
   ```bash
   bash scripts/fix_permissions.sh
   ```

4. Ask user to log out/in again

### Adding New Roles

If you add a new role:
1. Create it in the admin panel with permissions
2. The system handles the rest automatically
3. Users with that role will get permissions on login

### Changing Permissions

When you modify permissions in admin panel:
1. Changes are saved immediately
2. Active users need to log out/in to get new permissions
3. New logins automatically get the latest permissions

## Documentation

- **[PERMISSION_FIX_USER_GUIDE.md](PERMISSION_FIX_USER_GUIDE.md)** - User-friendly explanation
- **[PERMISSION_FIX_SUMMARY.md](PERMISSION_FIX_SUMMARY.md)** - Technical details
- **[README_PERMISSIONS.md](README_PERMISSIONS.md)** - This file

## Test Results

Last test run (all passed ✅):

**Supervisor:**
- ✅ View templates, forms, submissions
- ✅ Review submissions
- ✅ Correctly blocked from creating submissions/users

**Fieldman:**
- ✅ View templates, forms
- ✅ Create, view, update, delete submissions
- ✅ Correctly blocked from reviewing/managing users

**30 users synced successfully**
**14 permission tests: All PASSED**
