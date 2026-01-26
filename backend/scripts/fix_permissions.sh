#!/bin/bash

# Fix Permission Issues Script
# This script ensures that all roles have proper permissions 
# and all users have their roles synced to Casbin

echo "🔧 Starting permission fix process..."

cd "$(dirname "$0")/.."

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

echo ""
echo "📝 Step 1: Ensuring role permissions are set..."
python3 scripts/ensure_permissions.py

if [ $? -ne 0 ]; then
    echo "❌ Failed to set role permissions"
    exit 1
fi

echo ""
echo "👥 Step 2: Syncing all users' roles to Casbin..."
python3 scripts/sync_user_roles.py

if [ $? -ne 0 ]; then
    echo "❌ Failed to sync user roles"
    exit 1
fi

echo ""
echo "✅ Permission fix completed successfully!"
echo ""
echo "📋 Summary:"
echo "  - Role permissions have been set in database and Casbin"
echo "  - All users have been synced with their roles in Casbin"
echo ""
echo "⚠️ Important: If the application is running, you should restart it"
echo "   or ask affected users to log out and log in again."
