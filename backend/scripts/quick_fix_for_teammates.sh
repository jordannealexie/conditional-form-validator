#!/bin/bash
# Quick Fix for Teammates - Permission Issues
# Run this script and then ask users to refresh their browsers

echo "🔧 Fixing permissions for all users..."
echo ""

cd "$(dirname "$0")/.."

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

echo "Step 1: Syncing all user roles..."
python3 scripts/sync_user_roles.py

echo ""
echo "Step 2: Testing a sample user..."
python3 -c "
import asyncio
from app.db.session import AsyncSessionLocal
from app.models.user import User
from app.core.casbin_enforcer import casbin_enforcer
from sqlalchemy import select

async def quick_test():
    await casbin_enforcer.initialize()
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.user_role == 'fieldman').limit(1)
        )
        user = result.scalar_one_or_none()
        if user:
            has_perm = await casbin_enforcer.check_rbac_permission_async(
                user.username, 'submissions', 'create'
            )
            print(f'✓ Test user {user.username} has submissions:create = {has_perm}')
            if not has_perm:
                print('⚠️  WARNING: User should have permission but does not!')
        else:
            print('⚠️  No fieldman users found for testing')

asyncio.run(quick_test())
"

echo ""
echo "✅ Backend is ready!"
echo ""
echo "📢 IMPORTANT: Tell your teammates to:"
echo "   1. Log out completely"
echo "   2. Hard refresh browser (Ctrl+Shift+R or Cmd+Shift+R)"
echo "   3. Clear browser cache if needed"
echo "   4. Log in again"
echo ""
echo "If still not working, restart the server."
