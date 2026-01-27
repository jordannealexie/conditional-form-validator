# 🔧 URGENT FIX FOR TEAMMATES

## Problem Found & Fixed
The permissions in the database were corrupted/wrong. This has been fixed now.

## What You Fixed
Ran `scripts/ensure_permissions.py` which reset all role permissions to correct defaults.

## Steps for Your Teammate

### Step 1: They Must Log Out
Tell them to **log out completely** from the application.

### Step 2: Clear Browser Cache (CRITICAL!)
They MUST do a hard refresh:

**Windows/Linux:**
- Press `Ctrl + Shift + R` OR
- Press `Ctrl + F5`

**Mac:**
- Press `Cmd + Shift + R`

**Or clear cache manually:**
- Chrome: Settings → Privacy → Clear browsing data → Cached images and files
- Firefox: Settings → Privacy → Clear Data → Cached Web Content
- Edge: Settings → Privacy → Clear browsing data

### Step 3: Log In Again
After clearing cache, log in with their credentials.

### Step 4: Test
Click "Apply Now" on any template. Should work now! ✅

## Why This Happened
Someone (or something) changed the fieldman role permissions in the database admin panel to include wrong permissions (users, roles, banks) instead of the correct ones (submissions, templates).

## To Prevent This
- Be careful when editing role permissions in the admin panel
- Use the admin panel's permission checkboxes, don't manually edit
- If unsure, run: `cd backend && python3 scripts/ensure_permissions.py`

## Verification
The permissions are now correct:
- ✅ fieldman: Can create/read/update/delete submissions, read templates
- ✅ supervisor: Can read submissions/templates, review submissions
- ✅ admin: Has all permissions

## If Still Not Working

1. **Check server is running:**
   ```bash
   ps aux | grep uvicorn
   ```

2. **Restart the server** (it should auto-reload but just in case):
   ```bash
   # Stop the server, then start it again
   ```

3. **Check browser console for errors:**
   - Press F12
   - Go to Console tab
   - Look for any red errors

4. **Verify permissions:**
   ```bash
   cd backend
   source venv/bin/activate
   python3 scripts/check_user_access.py <their_username> submissions create
   ```

5. **Run full fix:**
   ```bash
   cd backend
   bash scripts/fix_permissions.sh
   ```

## Summary for Teammate
**"The backend permissions were wrong and have been fixed. You need to:**
1. **Log out**
2. **Hard refresh browser (Ctrl+Shift+R)**
3. **Log in again"**

That's it!
