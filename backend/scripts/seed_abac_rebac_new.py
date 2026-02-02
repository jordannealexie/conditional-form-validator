"""
Seed ABAC and ReBAC Sample Data - Connected to Real Users
Creates realistic sample policies and relationships for testing
"""
import asyncio
import sys
import os
from pathlib import Path

# Set environment variables for database connection before importing app modules
os.environ.setdefault("POSTGRES_SERVER", "localhost:5434")
os.environ.setdefault("POSTGRES_USER", "postgres")
os.environ.setdefault("POSTGRES_PASSWORD", "postgres")
os.environ.setdefault("POSTGRES_DB", "fastapi_db")

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

print("Importing modules...")

from sqlalchemy import text, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import AsyncSessionLocal
from app.models.user import User, ResourceRelationship
from app.models.abac import ABACPolicy, UserAttribute, ResourceAttribute
from app.models.forms import FormTemplate, FormSubmission


async def seed_all():
    """Main seeding function"""
    async with AsyncSessionLocal() as db:
        await seed_abac_policies(db)
        await seed_user_attributes(db)
        await seed_resource_attributes(db)
        await seed_rebac_relationships(db)


async def seed_abac_policies(db: AsyncSession):
    """Seed realistic ABAC policies"""
    print("🔐 Seeding ABAC Policies...")
    
    # Delete existing
    await db.execute(text("DELETE FROM abac_policies"))
    await db.commit()
    
    policies = [
        {
            "name": "Admin Full Access",
            "description": "Admins have full access to all resources",
            "rules": {
                "condition": "all",
                "rules": [
                    {"field": "user.role", "operator": "==", "value": "admin"}
                ]
            },
            "is_active": True
        },
        {
            "name": "Supervisor Read Access",
            "description": "Supervisors can read submissions and templates",
            "rules": {
                "condition": "all",
                "rules": [
                    {"field": "user.role", "operator": "==", "value": "supervisor"}
                ]
            },
            "is_active": True
        },
        {
            "name": "Own Submissions Only",
            "description": "Users can only access their own submissions",
            "rules": {
                "condition": "all",
                "rules": [
                    {"field": "user.id", "operator": "==", "value": "resource.user_id"}
                ]
            },
            "is_active": True
        },
        {
            "name": "Same Bank Access",
            "description": "Users can only access templates from their bank",
            "rules": {
                "condition": "all",
                "rules": [
                    {"field": "user.bank_id", "operator": "==", "value": "resource.bank_id"}
                ]
            },
            "is_active": True
        }
    ]
    
    for policy_data in policies:
        db.add(ABACPolicy(**policy_data))
    
    await db.commit()
    print(f"   ✅ Created {len(policies)} ABAC policies")


async def seed_user_attributes(db: AsyncSession):
    """Seed user attributes connected to real users"""
    print("👤 Seeding User Attributes...")
    
    # Delete existing
    await db.execute(text("DELETE FROM user_attributes"))
    await db.commit()
    
    # Get real users
    result = await db.execute(select(User).limit(10))
    users = result.scalars().all()
    
    if not users:
        print("   ⚠️  No users found. Skipping...")
        return
    
    attributes_data = []
    for user in users:
        if user.user_role == 'admin':
            dept, level, clearance = 'administration', '10', 'full'
        elif user.user_role == 'supervisor':
            dept, level, clearance = 'operations', '7', 'high'
        else:
            dept, level, clearance = 'field_operations', '3', 'standard'
        
        attributes_data.extend([
            {"user_id": user.id, "attribute_key": "department", "attribute_value": dept},
            {"user_id": user.id, "attribute_key": "level", "attribute_value": level},
            {"user_id": user.id, "attribute_key": "clearance", "attribute_value": clearance},
            {"user_id": user.id, "attribute_key": "role", "attribute_value": user.user_role},
        ])
    
    for attr_data in attributes_data:
        db.add(UserAttribute(**attr_data))
    
    await db.commit()
    print(f"   ✅ Created {len(attributes_data)} user attributes")


async def seed_resource_attributes(db: AsyncSession):
    """Seed resource attributes for templates and submissions"""
    print("📦 Seeding Resource Attributes...")
    
    # Delete existing
    await db.execute(text("DELETE FROM resource_attributes"))
    await db.commit()
    
    # Get templates
    templates_result = await db.execute(select(FormTemplate).limit(5))
    templates = templates_result.scalars().all()
    
    # Get submissions
    submissions_result = await db.execute(select(FormSubmission).limit(5))
    submissions = submissions_result.scalars().all()
    
    attributes_data = []
    
    # Add attributes to templates
    for i, template in enumerate(templates):
        classification = "public" if i % 2 == 0 else "confidential"
        attributes_data.extend([
            {"resource_type": "template", "resource_id": str(template.id), 
             "attribute_key": "classification", "attribute_value": classification},
            {"resource_type": "template", "resource_id": str(template.id), 
             "attribute_key": "bank_id", "attribute_value": str(template.bank_id or 1)},
        ])
    
    # Add attributes to submissions
    for submission in submissions:
        attributes_data.extend([
            {"resource_type": "submission", "resource_id": str(submission.id), 
             "attribute_key": "user_id", "attribute_value": str(submission.user_id)},
            {"resource_type": "submission", "resource_id": str(submission.id), 
             "attribute_key": "status", "attribute_value": submission.status or "pending"},
        ])
    
    for attr_data in attributes_data:
        db.add(ResourceAttribute(**attr_data))
    
    await db.commit()
    print(f"   ✅ Created {len(attributes_data)} resource attributes")


async def seed_rebac_relationships(db: AsyncSession):
    """Seed ReBAC relationships"""
    print("🔗 Seeding ReBAC Relationships...")
    
    # Delete existing
    await db.execute(text("DELETE FROM resource_relationships"))
    await db.commit()
    
    # Get real data
    users_result = await db.execute(select(User).limit(10))
    users = users_result.scalars().all()
    
    templates_result = await db.execute(select(FormTemplate).limit(5))
    templates = templates_result.scalars().all()
    
    submissions_result = await db.execute(select(FormSubmission).limit(5))
    submissions = submissions_result.scalars().all()
    
    if not users:
        print("   ⚠️  No users found. Skipping...")
        return
    
    relationships_data = []
    
    # User owns template relationships
    for i, template in enumerate(templates[:3]):
        if i < len(users):
            relationships_data.append({
                "subject_type": "user",
                "subject_id": str(users[i].id),
                "relationship_type": "owner",
                "resource_type": "template",
                "resource_id": str(template.id),
                "parent_resource_type": "bank",
                "parent_resource_id": str(template.bank_id or 1)
            })
    
    # User can view template relationships
    for i, template in enumerate(templates):
        for j in range(min(3, len(users))):
            relationships_data.append({
                "subject_type": "user",
                "subject_id": str(users[j].id),
                "relationship_type": "viewer",
                "resource_type": "template",
                "resource_id": str(template.id),
                "parent_resource_type": "bank",
                "parent_resource_id": str(template.bank_id or 1)
            })
    
    # User owns submission relationships
    for submission in submissions:
        relationships_data.append({
            "subject_type": "user",
            "subject_id": str(submission.user_id),
            "relationship_type": "owner",
            "resource_type": "submission",
            "resource_id": str(submission.id),
            "parent_resource_type": "template",
            "parent_resource_id": str(submission.template_id)
        })
    
    # Role can manage resource relationships
    if users:
        admin_users = [u for u in users if u.user_role == 'admin']
        if admin_users and templates:
            relationships_data.append({
                "subject_type": "role",
                "subject_id": "admin",
                "relationship_type": "manager",
                "resource_type": "template",
                "resource_id": str(templates[0].id),
                "parent_resource_type": "bank",
                "parent_resource_id": str(templates[0].bank_id or 1)
            })
    
    for rel_data in relationships_data:
        db.add(ResourceRelationship(**rel_data))
    
    await db.commit()
    print(f"   ✅ Created {len(relationships_data)} ReBAC relationships")


if __name__ == "__main__":
    # Deprecated entrypoint: delegate to unified template seeding so
    # there is only one seed implementation teammates need to use.
    from seed_all_templates import seed_all_templates

    asyncio.run(seed_all_templates())
