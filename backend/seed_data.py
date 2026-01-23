import asyncio
import sys
import uuid
from pathlib import Path
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload

# Add project root to path
backend_path = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_path))

from app.db.session import AsyncSessionLocal
from app.models.user import User, Role, user_roles, RefreshToken, ResourceRelationship
from app.models.forms import Bank, FormTemplate, FormSubmission, FormFile
from app.models.audit import AuditLog
from app.models.abac import UserAttribute, ResourceAttribute, ABACPolicy
from app.core.security import get_password_hash
from app.core.casbin_enforcer import casbin_enforcer, CasbinRule

# --- FORM TEMPLATE DEFINITIONS ---

BDO_TEMPLATE = {
    "name": "BDO Loan Application Form",
    "version": "1.0.0",
    "fields": [
        {"id": "applicant_name", "label": "Full Name", "type": "text", "required": True},
        {"id": "email", "label": "Email Address", "type": "email", "required": True},
        {"id": "phone", "label": "Mobile Number", "type": "text", "required": True},
        {"id": "civil_status", "label": "Civil Status", "type": "select", "required": True, "options": ["Single", "Married", "Divorced", "Widowed"]},
        {"id": "spouse_name", "label": "Spouse Name", "type": "text", "required": True, "show_if": {"field": "civil_status", "operator": "equals", "value": "Married"}},
        {"id": "employment_status", "label": "Employment Status", "type": "select", "required": True, "options": ["Employed", "Self-Employed", "Unemployed", "Retired"]},
        {"id": "employer_name", "label": "Employer Name", "type": "text", "required": True, "show_if": {"field": "employment_status", "operator": "equals", "value": "Employed"}},
        {"id": "monthly_income", "label": "Monthly Income (PHP)", "type": "number", "required": True},
        {"id": "loan_amount", "label": "Loan Amount (PHP)", "type": "number", "required": True},
        {"id": "loan_purpose", "label": "Purpose of Loan", "type": "select", "required": True, "options": ["Home Renovation", "Education", "Medical", "Business", "Car Purchase"]},
        {"id": "has_collateral", "label": "Do you have collateral?", "type": "checkbox", "default_value": False},
        {"id": "collateral_type", "label": "Collateral Type", "type": "select", "required": True, "options": ["Real Estate", "Vehicle", "Deposits"], "show_if": {"field": "has_collateral", "operator": "equals", "value": True}},
        {"id": "valid_id", "label": "Valid Government ID", "type": "file", "required": True},
        {"id": "proof_of_income", "label": "Proof of Income (COE/Pay Slip)", "type": "file", "required": True}
    ],
    "schema_json": {
        "type": "object",
        "properties": {
            "applicant_name": {"type": "string", "minLength": 3},
            "email": {"type": "string", "format": "email"},
            "phone": {"type": "string", "pattern": "^09\\d{9}$"},
            "civil_status": {"type": "string", "enum": ["Single", "Married", "Divorced", "Widowed"]},
            "spouse_name": {"type": "string"},
            "employment_status": {"type": "string", "enum": ["Employed", "Self-Employed", "Unemployed", "Retired"]},
            "employer_name": {"type": "string"},
            "monthly_income": {"type": "number", "minimum": 15000},
            "loan_amount": {"type": "number", "minimum": 50000},
            "loan_purpose": {"type": "string"},
            "has_collateral": {"type": "boolean"},
            "collateral_type": {"type": "string"},
            "valid_id": {"type": "string"},
            "proof_of_income": {"type": "string"}
        },
        "required": ["applicant_name", "email", "phone", "civil_status", "employment_status", "monthly_income", "loan_amount", "loan_purpose", "valid_id", "proof_of_income"]
    }
}

MAYA_TEMPLATE = {
    "name": "Maya Digital Credit Line",
    "version": "1.2.0",
    "fields": [
        {"id": "legal_name", "label": "Legal Name (as per ID)", "type": "text", "required": True},
        {"id": "maya_id", "label": "Maya ID / Number", "type": "text", "required": True},
        {"id": "birthdate", "label": "Date of Birth", "type": "date", "required": True},
        {"id": "requested_credit", "label": "Requested Credit Limit", "type": "number", "required": True},
        {"id": "use_case", "label": "How will you use Maya Credit?", "type": "select", "required": True, "options": ["Daily Expenses", "Bills", "Shopping", "Emergency"]},
        {"id": "is_regular_user", "label": "Are you a frequent Maya user?", "type": "checkbox", "default_value": True},
        {"id": "average_monthly_spend", "label": "Avg Monthly Spend", "type": "number", "required": True, "show_if": {"field": "is_regular_user", "operator": "equals", "value": True}},
        {"id": "id_type", "label": "Primary ID Type", "type": "select", "required": True, "options": ["UMID", "Driver License", "Passport", "SSS"]},
        {"id": "id_front", "label": "ID Front Photo", "type": "file", "required": True},
        {"id": "id_back", "label": "ID Back Photo", "type": "file", "required": True},
        {"id": "selfie_verification", "label": "Selfie with ID", "type": "file", "required": True}
    ],
    "schema_json": {
        "type": "object",
        "properties": {
            "legal_name": {"type": "string"},
            "maya_id": {"type": "string"},
            "birthdate": {"type": "string", "format": "date"},
            "requested_credit": {"type": "number", "minimum": 1000, "maximum": 100000},
            "use_case": {"type": "string"},
            "is_regular_user": {"type": "boolean"},
            "average_monthly_spend": {"type": "number"},
            "id_type": {"type": "string"},
            "id_front": {"type": "string"},
            "id_back": {"type": "string"},
            "selfie_verification": {"type": "string"}
        },
        "required": ["legal_name", "maya_id", "birthdate", "requested_credit", "use_case", "id_type", "id_front", "id_back", "selfie_verification"]
    }
}

SECB_TEMPLATE = {
    "name": "Security Bank Gold Mastery Card",
    "version": "2.0.1",
    "fields": [
        {"id": "customer_name", "label": "Customer Full Name", "type": "text", "required": True},
        {"id": "tin_number", "label": "TIN Number", "type": "text", "required": True},
        {"id": "source_of_funds", "label": "Source of Funds", "type": "select", "required": True, "options": ["Salary", "Business", "Investment", "Remittance"]},
        {"id": "annual_income", "label": "Annual Gross Income", "type": "number", "required": True},
        {"id": "existing_client", "label": "Are you an existing client?", "type": "checkbox", "default_value": False},
        {"id": "account_number", "label": "Account Number", "type": "text", "required": True, "show_if": {"field": "existing_client", "operator": "equals", "value": True}},
        {"id": "address_line1", "label": "Address Line 1", "type": "text", "required": True},
        {"id": "city", "label": "City", "type": "text", "required": True},
        {"id": "postal_code", "label": "Postal Code", "type": "text", "required": True},
        {"id": "emergency_contact", "label": "Emergency Contact Name", "type": "text", "required": True},
        {"id": "emergency_number", "label": "Emergency Contact Number", "type": "text", "required": True},
        {"id": "itr_copy", "label": "ITR Copy", "type": "file", "required": True},
        {"id": "valid_id_copy", "label": "Valid ID Copy", "type": "file", "required": True}
    ],
    "schema_json": {
        "type": "object",
        "properties": {
            "customer_name": {"type": "string"},
            "tin_number": {"type": "string", "pattern": "^\\d{3}-\\d{3}-\\d{3}-\\d{3}$"},
            "source_of_funds": {"type": "string"},
            "annual_income": {"type": "number", "minimum": 400000},
            "existing_client": {"type": "boolean"},
            "account_number": {"type": "string"},
            "address_line1": {"type": "string"},
            "city": {"type": "string"},
            "postal_code": {"type": "string"},
            "emergency_contact": {"type": "string"},
            "emergency_number": {"type": "string"},
            "itr_copy": {"type": "string"},
            "valid_id_copy": {"type": "string"}
        },
        "required": ["customer_name", "tin_number", "source_of_funds", "annual_income", "address_line1", "city", "postal_code", "itr_copy", "valid_id_copy"]
    }
}

# --- SEEDING LOGIC ---

async def seed_data():
    print("🚀 Starting seed_data function...")
    async with AsyncSessionLocal() as session:
        print("🌱 Starting data seeding...")
        # 0. Clean up existing data in correct order to handle FKs
        print("🧹 Cleaning up existing data...")
        await session.execute(delete(AuditLog))
        await session.execute(delete(FormFile))
        await session.execute(delete(FormSubmission))
        await session.execute(delete(RefreshToken))
        await session.execute(delete(UserAttribute))
        await session.execute(delete(ResourceAttribute))
        await session.execute(delete(ABACPolicy))
        await session.execute(delete(ResourceRelationship))
        await session.execute(delete(user_roles))
        await session.execute(delete(FormTemplate))
        await session.execute(delete(User))
        await session.execute(delete(Bank))
        await session.execute(delete(Role))
        await session.execute(delete(CasbinRule))
        await session.commit()
        
        # 2. Seed Banks
        print("🏦 Seeding banks...")
        banks_data = [
            {"name": "BDO Unibank", "code": "BDO", "logo_url": "https://www.bdo.com.ph/sites/default/files/styles/logo/public/bdo-logo.png", "primary_color": "#005baa", "description": "Leading bank in PH", "active": True},
            {"name": "Maya Bank", "code": "MAYA", "logo_url": "https://www.maya.ph/hubfs/Maya-Logo-2022.svg", "primary_color": "#2ecc71", "description": "Digital bank for the modern age", "active": True},
            {"name": "Security Bank", "code": "SECB", "logo_url": "https://www.securitybank.com/wp-content/uploads/2021/03/logo-sb-header.png", "primary_color": "#000000", "description": "BetterBanking experiences", "active": True}
        ]
        banks = []
        for b_data in banks_data:
            bank = Bank(**b_data)
            session.add(bank)
            banks.append(bank)
        await session.flush()

        # 3. Seed Roles (Consolidated JSONB format)
        print("🔑 Seeding roles...")
        role_definitions = [
            {
                "name": "admin", 
                "description": "Full system access", 
                "permissions": [
                    "users:read", "users:write", "templates:read", "templates:write",
                    "submissions:read", "submissions:write", "submissions:review",
                    "roles:read", "roles:write", "banks:read", "banks:write"
                ]
            },
            {
                "name": "supervisor", 
                "description": "View and review submissions", 
                "permissions": ["submissions:read", "submissions:review", "templates:read"]
            },
            {
                "name": "fieldman", 
                "description": "Submit and view own forms", 
                "permissions": ["submissions:create", "submissions:read_own", "templates:read"]
            }
        ]
        roles = {}
        for r_def in role_definitions:
            role = Role(**r_def)
            session.add(role)
            roles[r_def["name"]] = role
        await session.flush()
        
        # Initialize Casbin Enforcer for seeding
        await casbin_enforcer.initialize()
        
        # Sync role permissions to Casbin
        print("🔄 Syncing role permissions to Casbin...")
        for r_name, role_obj in roles.items():
            casbin_enforcer.sync_role_permissions(r_name, role_obj.permissions or [])
        
        # 4. Seed Users (27 users total)
        print("👤 Seeding users...")
        password_hash = get_password_hash("password123")
        
        for bank in banks:
            for role_name in ["admin", "supervisor", "fieldman"]:
                for i in range(1, 4):
                    username = f"{bank.code.lower()}_{role_name}_{i}"
                    user = User(
                        username=username,
                        email=f"{username}@example.com",
                        password_hash=password_hash,
                        user_role=role_name,
                        bank_id=bank.id,
                        first_name=f"{bank.code}",
                        last_name=f"{role_name.capitalize()} {i}",
                        full_name=f"{bank.code} {role_name.capitalize()} {i}",
                        department="Operations",
                        level=i,
                        location="Manila",
                        active=True
                    )
                    user.roles = [roles[role_name]]
                    session.add(user)
         
        # 5. Seed Specific Admin (harrypotter)
        print("🧙 Seeding harrypotter...")
        hp = User(
            username="harrypotter",
            email="harrypotter@example.com",
            password_hash=get_password_hash("harrypotter"),
            user_role="admin",
            first_name="Harry",
            last_name="Potter",
            full_name="Harry Potter",
            department="IT",
            level=5,
            location="Parañaque",
            active=True,
            is_superuser=True
        )
        hp.roles = [roles["admin"]]
        session.add(hp)

        # 6. Seed Templates
        print("📝 Seeding templates...")
        template_maps = [
            (banks[0].id, BDO_TEMPLATE),
            (banks[1].id, MAYA_TEMPLATE),
            (banks[2].id, SECB_TEMPLATE)
        ]
        
        for bank_id, t_def in template_maps:
            template = FormTemplate(
                bank_id=bank_id,
                name=t_def["name"],
                version=t_def["version"],
                schema_json=t_def["schema_json"],
                fields=t_def["fields"],
                active=True,
                created_by="system_seeder"
            )
            session.add(template)

        await session.flush()

        # Sync user roles to Casbin for all seeded users
        print("🔄 Syncing user roles to Casbin...")
        result = await session.execute(select(User))
        seeded_users = result.scalars().all()
        for u in seeded_users:
            if u.user_role:
                casbin_enforcer.sync_user_roles(u.username, [u.user_role])

        await session.commit()
        print("✅ Data seeding completed successfully!")

if __name__ == "__main__":
    asyncio.run(seed_data())

