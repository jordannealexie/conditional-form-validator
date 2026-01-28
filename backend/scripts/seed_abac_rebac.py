"""
Seed ABAC and ReBAC Sample Policies
Creates sample attribute-based and relationship-based access control policies
"""
import asyncio
import sys
import os

# Add parent directory to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import AsyncSessionLocal, engine
from app.models.user import User, ResourceRelationship
from app.models.abac import ABACPolicy, UserAttribute, ResourceAttribute


async def seed_abac_policies(db: AsyncSession):
    """Seed sample ABAC policies connected to real data"""
    print("🔐 Seeding ABAC Policies...")
    
    # Delete existing policies to recreate with new samples
    await db.execute(text("DELETE FROM abac_policies"))
    await db.commit()
    print("   🗑️  Cleared existing ABAC policies")
    
    # Sample ABAC Policies - Realistic for testing - Realistic for testing
    policies = [
        {
            "name": "Admin Full Access",
            "description": "Admins have full access to all resources",
            "rules": {
                "condition": "all",
                "rules": [
                    {
                        "field": "user.role",
                        "operator": "==",
                        "value": "admin"
                    }
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
                    {
                        "field": "user.role",
                        "operator": "==",
                        "value": "supervisor"
                    }
                ]
            },
            "is_active": True
        },
        {
            "name": "Fieldman Own Submissions",
            "description": "Fieldman can only access their own submissions",
            "rules": {
                "condition": "all",
                "rules": [
                    {
                        "field": "user.role",
                        "operator": "==",
                        "value": "fieldman"
                    },
                    {
                        "field": "user.id",
                        "operator": "==",
                        "value": "resource.user_id"
                    }
                ]
            },
            "is_active": True
        },
        {
            "name": "Same Bank Access",
            "description": "Users can only access templates from their own bank",
            "rules": {
                "condition": "all",
                "rules": [
                    {
                        "field": "user.bank_id",
                        "operator": "==",
                        "value": "resource.bank_id"
                    }
                ]
            },
            "is_active": True
        }
    ]
    
    for policy_data in policies:
        policy = ABACPolicy(**policy_data)
        db.add(policy)
    
    await db.commit()
    print(f"   ✅ Created {len(policies)} ABAC policies")


async def seed_user_attributes(db: AsyncSession):
    """Seed sample user attributes connected to real users"""
    print("👤 Seeding User Attributes...")
    
    # Delete existing attributes
    await db.execute(text("DELETE FROM user_attributes"))
    await db.commit()
    print("   🗑️  Cleared existing user attributes")
    
    # Get real users from database
    result = await db.execute(select(User).limit(10))
    users = result.scalars().all()
    
    if not users:
        print("   ⚠️  No users found. Please seed users first.")
        return
    
    # Check if attributes already exist
    result = await db.execute(select(UserAttribute))
    existing_attributes = result.scalars().all()
    
    if existing_attributes:
        print("   ℹ️  User attributes already exist. Skipping...")
        return
    
    # Sample attributes for different users
    attributes_data = [
        # User 1: Department Manager
        {"user_id": users[0].id, "attribute_key": "department", "attribute_value": "engineering"},
        {"user_id": users[0].id, "attribute_key": "level", "attribute_value": "7"},
        {"user_id": users[0].id, "attribute_key": "position", "attribute_value": "manager"},
        {"user_id": users[0].id, "attribute_key": "clearance", "attribute_value": "confidential"},
        {"user_id": users[0].id, "attribute_key": "region", "attribute_value": "north"},
        {"user_id": users[0].id, "attribute_key": "is_global", "attribute_value": "false"},
    ]
    
    if len(users) > 1:
        # User 2: Junior Staff
        attributes_data.extend([
            {"user_id": users[1].id, "attribute_key": "department", "attribute_value": "engineering"},
            {"user_id": users[1].id, "attribute_key": "level", "attribute_value": "3"},
            {"user_id": users[1].id, "attribute_key": "position", "attribute_value": "developer"},
            {"user_id": users[1].id, "attribute_key": "clearance", "attribute_value": "public"},
            {"user_id": users[1].id, "attribute_key": "region", "attribute_value": "north"},
            {"user_id": users[1].id, "attribute_key": "is_global", "attribute_value": "false"},
        ])
    
    if len(users) > 2:
        # User 3: Sales Department
        attributes_data.extend([
            {"user_id": users[2].id, "attribute_key": "department", "attribute_value": "sales"},
            {"user_id": users[2].id, "attribute_key": "level", "attribute_value": "5"},
            {"user_id": users[2].id, "attribute_key": "position", "attribute_value": "sales_rep"},
            {"user_id": users[2].id, "attribute_key": "clearance", "attribute_value": "public"},
            {"user_id": users[2].id, "attribute_key": "region", "attribute_value": "south"},
            {"user_id": users[2].id, "attribute_key": "is_global", "attribute_value": "false"},
        ])
    
    if len(users) > 3:
        # User 4: Global Admin
        attributes_data.extend([
            {"user_id": users[3].id, "attribute_key": "department", "attribute_value": "operations"},
            {"user_id": users[3].id, "attribute_key": "level", "attribute_value": "9"},
            {"user_id": users[3].id, "attribute_key": "position", "attribute_value": "director"},
            {"user_id": users[3].id, "attribute_key": "clearance", "attribute_value": "top_secret"},
            {"user_id": users[3].id, "attribute_key": "region", "attribute_value": "north"},
            {"user_id": users[3].id, "attribute_key": "is_global", "attribute_value": "true"},
        ])
    
    for attr_data in attributes_data:
        attribute = UserAttribute(**attr_data)
        db.add(attribute)
    
    await db.commit()
    print(f"   ✅ Created {len(attributes_data)} user attributes for {len(users)} users")


async def seed_resource_attributes(db: AsyncSession):
    """Seed sample resource attributes"""
    print("📦 Seeding Resource Attributes...")
    
    # Check if attributes already exist
    result = await db.execute(select(ResourceAttribute))
    existing_attributes = result.scalars().all()
    
    if existing_attributes:
        print("   ℹ️  Resource attributes already exist. Skipping...")
        return
    
    # Sample resource attributes
    attributes_data = [
        # Template 1 - Engineering Document
        {"resource_type": "template", "resource_id": "1", "attribute_key": "department", "attribute_value": "engineering"},
        {"resource_type": "template", "resource_id": "1", "attribute_key": "classification", "attribute_value": "confidential"},
        {"resource_type": "template", "resource_id": "1", "attribute_key": "region", "attribute_value": "north"},
        
        # Template 2 - Public Form
        {"resource_type": "template", "resource_id": "2", "attribute_key": "department", "attribute_value": "sales"},
        {"resource_type": "template", "resource_id": "2", "attribute_key": "classification", "attribute_value": "public"},
        {"resource_type": "template", "resource_id": "2", "attribute_key": "region", "attribute_value": "south"},
        
        # Template 3 - HR Document
        {"resource_type": "template", "resource_id": "3", "attribute_key": "department", "attribute_value": "hr"},
        {"resource_type": "template", "resource_id": "3", "attribute_key": "classification", "attribute_value": "confidential"},
        {"resource_type": "template", "resource_id": "3", "attribute_key": "region", "attribute_value": "north"},
        
        # Submission 1
        {"resource_type": "submission", "resource_id": "1", "attribute_key": "department", "attribute_value": "engineering"},
        {"resource_type": "submission", "resource_id": "1", "attribute_key": "classification", "attribute_value": "public"},
        {"resource_type": "submission", "resource_id": "1", "attribute_key": "region", "attribute_value": "north"},
    ]
    
    for attr_data in attributes_data:
        attribute = ResourceAttribute(**attr_data)
        db.add(attribute)
    
    await db.commit()
    print(f"   ✅ Created {len(attributes_data)} resource attributes")


async def seed_rebac_relationships(db: AsyncSession):
    """Seed sample ReBAC relationships"""
    print("🔗 Seeding ReBAC Relationships...")
    
    # Get users for relationships
    result = await db.execute(select(User).limit(5))
    users = result.scalars().all()
    
    if not users:
        print("   ⚠️  No users found. Please seed users first.")
        return
    
    # Check if relationships already exist
    result = await db.execute(select(ResourceRelationship))
    existing_relationships = result.scalars().all()
    
    if existing_relationships:
        print("   ℹ️  ReBAC relationships already exist. Skipping...")
        return
    
    # Sample relationships
    relationships_data = [
        # Organization hierarchy - top level resources use same type/id as parent
        {
            "subject_type": "user",
            "subject_id": str(users[0].id),
            "resource_type": "organization",
            "resource_id": "1",
            "parent_resource_type": "organization",
            "parent_resource_id": "1",
            "relationship_type": "member"
        },
        {
            "subject_type": "user",
            "subject_id": str(users[0].id),
            "resource_type": "team",
            "resource_id": "engineering",
            "parent_resource_type": "organization",
            "parent_resource_id": "1",
            "relationship_type": "manager"
        },
        
        # Template ownership
        {
            "subject_type": "user",
            "subject_id": str(users[0].id),
            "resource_type": "template",
            "resource_id": "1",
            "parent_resource_type": "team",
            "parent_resource_id": "engineering",
            "relationship_type": "owner"
        },
    ]
    
    if len(users) > 1:
        relationships_data.extend([
            # User 2 is member of engineering team
            {
                "subject_type": "user",
                "subject_id": str(users[1].id),
                "resource_type": "team",
                "resource_id": "engineering",
                "parent_resource_type": "organization",
                "parent_resource_id": "1",
                "relationship_type": "member"
            },
            # User 2 can view template 1
            {
                "subject_type": "user",
                "subject_id": str(users[1].id),
                "resource_type": "template",
                "resource_id": "1",
                "parent_resource_type": "team",
                "parent_resource_id": "engineering",
                "relationship_type": "viewer"
            },
        ])
    
    if len(users) > 2:
        relationships_data.extend([
            # User 3 is member of sales team
            {
                "subject_type": "user",
                "subject_id": str(users[2].id),
                "resource_type": "team",
                "resource_id": "sales",
                "parent_resource_type": "organization",
                "parent_resource_id": "1",
                "relationship_type": "manager"
            },
            # User 3 owns template 2
            {
                "subject_type": "user",
                "subject_id": str(users[2].id),
                "resource_type": "template",
                "resource_id": "2",
                "parent_resource_type": "team",
                "parent_resource_id": "sales",
                "relationship_type": "owner"
            },
        ])
    
    if len(users) > 3:
        relationships_data.extend([
            # User 4 is admin of organization
            {
                "subject_type": "user",
                "subject_id": str(users[3].id),
                "resource_type": "organization",
                "resource_id": "1",
                "parent_resource_type": "organization",
                "parent_resource_id": "1",
                "relationship_type": "admin"
            },
        ])
    
    for rel_data in relationships_data:
        relationship = ResourceRelationship(**rel_data)
        db.add(relationship)
    
    await db.commit()
    print(f"   ✅ Created {len(relationships_data)} ReBAC relationships")


async def main():
    """Main seeding function"""
    print("\n" + "="*60)
    print("🌱 ABAC & ReBAC Policy Seeding")
    print("="*60 + "\n")
    
    async with AsyncSessionLocal() as db:
        try:
            # Seed ABAC
            await seed_abac_policies(db)
            await seed_user_attributes(db)
            await seed_resource_attributes(db)
            
            # Seed ReBAC
            await seed_rebac_relationships(db)
            
            print("\n" + "="*60)
            print("✅ ABAC & ReBAC Seeding Complete!")
            print("="*60 + "\n")
            
        except Exception as e:
            print(f"\n❌ Error during seeding: {str(e)}")
            import traceback
            traceback.print_exc()
            await db.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(main())
