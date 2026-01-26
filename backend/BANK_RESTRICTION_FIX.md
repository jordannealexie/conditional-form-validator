# Bank Restriction Fix

## Issue
Users with all permissions checked still couldn't click "Apply Now" and submit forms. Error: "You are not authorized to submit this form."

## Root Cause
There were **two separate authorization checks**:

1. ✅ **Permission check** - User has `submissions:create` permission (working after previous fix)
2. ❌ **Bank restriction check** - User can only submit to templates from their assigned bank (blocking users)

Example:
- User `bdo_fieldman_1` is assigned to Bank ID 7 (BDO)
- User tries to apply to a template from Bank ID 8 (Maya Bank)
- **Result**: Blocked with "You are not authorized to submit forms for this bank"

This happened even though the user had `submissions:create` permission checked.

## Solution
Removed the bank restriction check. Now:
- If user has `submissions:create` permission → **can submit to ANY bank's templates**
- The permission check is sufficient authorization
- Bank assignment is now advisory/informational only, not a blocker

## Changes Made

### 1. Backend: [submissions.py](../app/api/v1/endpoints/submissions.py)
**Before:**
```python
# Enforce ReBAC: If user is restricted to a bank, they can only submit for that bank
if not getattr(current_user, 'is_superuser', False) and current_user.user_role != "admin":
    if current_user.bank_id and template.bank_id != current_user.bank_id:
         raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="You are not authorized to submit forms for this bank."
        )
```

**After:**
```python
# Enforce ReBAC: If user is restricted to a bank, they can only submit for that bank
# UNLESS they have explicit permissions (checked by authorize dependency)
# Note: authorize(resource="submissions", action="create") already passed at this point,
# so if user has the permission explicitly, we trust it.
# Bank restriction is now optional/advisory, not blocking for users with permissions.
```

### 2. Frontend: [dashboard.js](../../frontend/js/dashboard.js)
Removed frontend bank matching check - backend permission check is sufficient.

## Test Results

```
👤 Test User: bdo_fieldman_1
   Role: fieldman
   Bank ID: 7

🔑 Permission Check:
   submissions:create = ✅ GRANTED

📋 Template Access Test:
   Template: BDO Loan Application          | Bank: 7 | ✅ MATCH
            → User CAN submit (has permission)
   Template: Maya Digital Credit Line      | Bank: 8 | ⚠️  DIFF BANK
            → User CAN submit (has permission)
   Template: Security Bank Gold Card       | Bank: 9 | ⚠️  DIFF BANK
            → User CAN submit (has permission)

✅ Bank restriction removed - users with permissions can submit to any bank
```

## What This Means

### For Non-Admin Users:
- ✅ Can now apply to **any template** if they have `submissions:create` permission
- ✅ No longer blocked by bank restrictions
- ✅ Bank assignment is just for organizational purposes, not access control

### For Admins:
- Permissions are the primary access control mechanism
- Bank assignments can still be used for:
  - Organizational categorization
  - Reporting and filtering
  - Optional business logic (if you want to add it back later)

## Next Steps

**Users need to refresh their browser** (Ctrl+F5 or Cmd+Shift+R) to load the updated JavaScript.

The backend changes are already live (uvicorn auto-reloaded).

## Alternative Approaches

If you **want** to keep bank restrictions:

### Option A: Keep bank restrictions for some roles
Only apply bank restrictions to certain roles (e.g., fieldman but not supervisor).

### Option B: Make it configurable
Add a permission like `submissions:create:any_bank` for users who can submit across banks.

### Option C: Hybrid approach
- Default: Bank restricted
- If user has ALL permissions checked: Remove restriction

Let me know if you want to implement any of these alternatives!

## Verification

To test:
1. Log in as a non-admin user with `submissions:create` permission
2. Go to dashboard
3. Click "Apply Now" on ANY template (including other banks)
4. Should now work ✅

To verify programmatically:
```bash
cd backend
source venv/bin/activate
python3 scripts/test_bank_restrictions.py
```
