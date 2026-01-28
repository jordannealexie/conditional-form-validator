"""
Seed Data Script for Bank Templates
Creates comprehensive templates for BDO, Maya, and Security Bank with:
- 10-15 fields each
- Multiple field types (text, email, number, select, file, checkbox)
- Conditional logic with show_if (all/any/not operators)
- Validation rules
- File upload fields
"""
import asyncio
import sys
import os

# Add parent directory to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text, select
from app.db.session import AsyncSessionLocal, engine
from app.db.base_class import Base
from app.models.forms import Bank, FormTemplate, FormSubmission, SubmissionStatus
from app.models.user import User, ResourceRelationship, Role
from app.models.abac import ABACPolicy, UserAttribute, ResourceAttribute


# ============================================================================
# BDO Credit Card Application Template (15 fields)
# ============================================================================
def create_bdo_credit_card_template(bank_id: int):
    """BDO Credit Card Application with comprehensive fields and conditional logic"""
    
    fields = [
        {
            "id": "applicant_name",
            "type": "text",
            "label": "Full Name",
            "required": True,
            "validation": {"minLength": 2, "maxLength": 100},
            "placeholder": "Enter your full name"
        },
        {
            "id": "email",
            "type": "email",
            "label": "Email Address",
            "required": True,
            "validation": {"format": "email"},
            "placeholder": "your.email@example.com"
        },
        {
            "id": "mobile_number",
            "type": "text",
            "label": "Mobile Number",
            "required": True,
            "validation": {"pattern": "^09\\d{9}$"},
            "placeholder": "09123456789"
        },
        {
            "id": "date_of_birth",
            "type": "date",
            "label": "Date of Birth",
            "required": True
        },
        {
            "id": "annual_income",
            "type": "number",
            "label": "Annual Income (PHP)",
            "required": True,
            "validation": {"minimum": 150000, "maximum": 10000000},
            "show_if": {
                "field": "employment_status",
                "operator": "not_equals",
                "value": "Self-Employed"
            }
        },
        {
            "id": "employment_status",
            "type": "select",
            "label": "Employment Status",
            "required": True,
            "options": ["Employed", "Self-Employed", "Retired", "Unemployed"]
        },
        {
            "id": "company_name",
            "type": "text",
            "label": "Company Name",
            "required": True,
            "show_if": {
                "field": "employment_status",
                "operator": "equals",
                "value": "Employed"
            }
        },
        {
            "id": "business_name",
            "type": "text",
            "label": "Business Name",
            "required": True,
            "show_if": {
                "field": "employment_status",
                "operator": "equals",
                "value": "Self-Employed"
            }
        },
        {
            "id": "card_type",
            "type": "select",
            "label": "Preferred Card Type",
            "required": True,
            "options": ["Standard Mastercard", "Gold Mastercard", "Platinum Mastercard", "Titanium Mastercard"]
        },
        {
            "id": "existing_bdo_account",
            "type": "checkbox",
            "label": "I already have a BDO account",
            "required": False
        },
        {
            "id": "account_number",
            "type": "text",
            "label": "BDO Account Number",
            "required": True,
            "validation": {"pattern": "^\\d{10,12}$"},
            "placeholder": "Enter 10-12 digit account number",
            "show_if": {
                "field": "existing_bdo_account",
                "operator": "equals",
                "value": True
            }
        },
        {
            "id": "home_address",
            "type": "textarea",
            "label": "Home Address",
            "required": True,
            "validation": {"minLength": 10, "maxLength": 500},
            "rows": 3
        },
        {
            "id": "id_type",
            "type": "select",
            "label": "Valid ID Type",
            "required": True,
            "options": ["Philippine Passport", "Driver's License", "PRC ID", "SSS ID", "TIN ID", "Postal ID"]
        },
        {
            "id": "id_upload",
            "type": "file",
            "label": "Upload Valid ID",
            "required": True,
            "accept": "image/*,.pdf",
            "max_size_mb": 5
        },
        {
            "id": "income_proof_upload",
            "type": "file",
            "label": "Proof of Income",
            "required": True,
            "accept": "image/*,.pdf",
            "max_size_mb": 10,
            "show_if": {
                "field": "employment_status",
                "operator": "not_equals",
                "value": "Unemployed"
            }
        },
        {
            "id": "terms_accepted",
            "type": "checkbox",
            "label": "I agree to the terms and conditions",
            "required": True
        }
    ]
    
    schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "title": "BDO Credit Card Application",
        "properties": {
            "applicant_name": {
                "type": "string",
                "minLength": 2,
                "maxLength": 100
            },
            "email": {
                "type": "string",
                "format": "email"
            },
            "mobile_number": {
                "type": "string",
                "pattern": "^09\\d{9}$"
            },
            "date_of_birth": {
                "type": "string",
                "format": "date"
            },
            "annual_income": {
                "type": "number",
                "minimum": 150000,
                "maximum": 10000000
            },
            "employment_status": {
                "type": "string",
                "enum": ["Employed", "Self-Employed", "Retired", "Unemployed"]
            },
            "company_name": {"type": "string"},
            "business_name": {"type": "string"},
            "card_type": {
                "type": "string",
                "enum": ["Standard Mastercard", "Gold Mastercard", "Platinum Mastercard", "Titanium Mastercard"]
            },
            "existing_bdo_account": {"type": "boolean"},
            "account_number": {
                "type": "string",
                "pattern": "^\\d{10,12}$"
            },
            "home_address": {
                "type": "string",
                "minLength": 10,
                "maxLength": 500
            },
            "id_type": {
                "type": "string",
                "enum": ["Philippine Passport", "Driver's License", "PRC ID", "SSS ID", "TIN ID", "Postal ID"]
            },
            "id_upload": {"type": "string"},
            "income_proof_upload": {"type": "string"},
            "terms_accepted": {"type": "boolean"}
        },
        "required": [
            "applicant_name", "email", "mobile_number", "date_of_birth",
            "employment_status", "card_type", "home_address", "id_type",
            "id_upload", "terms_accepted"
        ]
    }
    
    ui_schema = {
        "ui:order": [
            "applicant_name", "email", "mobile_number", "date_of_birth",
            "employment_status", "company_name", "business_name", "annual_income",
            "card_type", "existing_bdo_account", "account_number",
            "home_address", "id_type", "id_upload", "income_proof_upload",
            "terms_accepted"
        ]
    }
    
    return {
        "bank_id": bank_id,
        "name": "BDO Credit Card Application",
        "form_type": "credit_card",
        "version": "1.0",
        "description": "Apply for a BDO credit card with our easy online application",
        "schema_json": schema,
        "fields": fields,
        "ui_schema": ui_schema,
        "active": True,
        "created_by": "system"
    }


# ============================================================================
# Maya Personal Loan Template (14 fields)
# ============================================================================
def create_maya_personal_loan_template(bank_id: int):
    """Maya Personal Loan with conditional logic based on loan amount"""
    
    fields = [
        {
            "id": "full_name",
            "type": "text",
            "label": "Full Name",
            "required": True,
            "validation": {"minLength": 2, "maxLength": 100}
        },
        {
            "id": "email",
            "type": "email",
            "label": "Email Address",
            "required": True
        },
        {
            "id": "mobile_number",
            "type": "text",
            "label": "Mobile Number",
            "required": True,
            "validation": {"pattern": "^09\\d{9}$"}
        },
        {
            "id": "date_of_birth",
            "type": "date",
            "label": "Date of Birth",
            "required": True
        },
        {
            "id": "civil_status",
            "type": "select",
            "label": "Civil Status",
            "required": True,
            "options": ["Single", "Married", "Divorced", "Widowed"]
        },
        {
            "id": "loan_amount",
            "type": "number",
            "label": "Loan Amount (PHP)",
            "required": True,
            "validation": {"minimum": 5000, "maximum": 50000, "multipleOf": 1000},
            "step": 1000
        },
        {
            "id": "loan_purpose",
            "type": "select",
            "label": "Purpose of Loan",
            "required": True,
            "options": ["Business Expansion", "Home Improvement", "Education", "Medical Expenses", "Debt Consolidation", "Personal Use", "Other"]
        },
        {
            "id": "loan_term",
            "type": "select",
            "label": "Preferred Loan Term",
            "required": True,
            "options": ["3 Months", "6 Months", "9 Months", "12 Months"]
        },
        {
            "id": "monthly_income",
            "type": "number",
            "label": "Monthly Income (PHP)",
            "required": True,
            "validation": {"minimum": 10000}
        },
        {
            "id": "source_of_income",
            "type": "select",
            "label": "Source of Income",
            "required": True,
            "options": ["Salary", "Business Income", "Freelance", "Investment", "Remittance", "Other"]
        },
        {
            "id": "is_maya_user",
            "type": "checkbox",
            "label": "I am an existing Maya user",
            "required": False
        },
        {
            "id": "maya_email",
            "type": "email",
            "label": "Maya Email Address",
            "required": False,
            "show_if": {
                "field": "is_maya_user",
                "operator": "equals",
                "value": True
            }
        },
        {
            "id": "government_id_upload",
            "type": "file",
            "label": "Government ID",
            "required": True,
            "accept": "image/*,.pdf",
            "max_size_mb": 5
        },
        {
            "id": "bank_statement_upload",
            "type": "file",
            "label": "3-Month Bank Statement",
            "required": False,
            "accept": "image/*,.pdf",
            "max_size_mb": 10,
            "show_if": {
                "all": [
                    {"field": "is_maya_user", "operator": "equals", "value": False},
                    {"field": "loan_amount", "operator": "greater_than", "value": 20000}
                ]
            }
        },
        {
            "id": "consent",
            "type": "checkbox",
            "label": "I authorize Maya to process my loan application and verify my information",
            "required": True
        }
    ]
    
    schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "title": "Maya Personal Loan Application",
        "properties": {
            "full_name": {"type": "string", "minLength": 2, "maxLength": 100},
            "email": {"type": "string", "format": "email"},
            "mobile_number": {"type": "string", "pattern": "^09\\d{9}$"},
            "date_of_birth": {"type": "string", "format": "date"},
            "civil_status": {"type": "string", "enum": ["Single", "Married", "Divorced", "Widowed"]},
            "loan_amount": {"type": "number", "minimum": 5000, "maximum": 50000, "multipleOf": 1000},
            "loan_purpose": {"type": "string", "enum": ["Business Expansion", "Home Improvement", "Education", "Medical Expenses", "Debt Consolidation", "Personal Use", "Other"]},
            "loan_term": {"type": "string", "enum": ["3 Months", "6 Months", "9 Months", "12 Months"]},
            "monthly_income": {"type": "number", "minimum": 10000},
            "source_of_income": {"type": "string", "enum": ["Salary", "Business Income", "Freelance", "Investment", "Remittance", "Other"]},
            "is_maya_user": {"type": "boolean"},
            "maya_email": {"type": "string", "format": "email"},
            "government_id_upload": {"type": "string"},
            "bank_statement_upload": {"type": "string"},
            "consent": {"type": "boolean"}
        },
        "required": [
            "full_name", "email", "mobile_number", "date_of_birth",
            "civil_status", "loan_amount", "loan_purpose", "loan_term",
            "monthly_income", "source_of_income", "government_id_upload", "consent"
        ]
    }
    
    ui_schema = {
        "ui:order": [
            "full_name", "email", "mobile_number", "date_of_birth",
            "civil_status", "loan_amount", "loan_purpose", "loan_term",
            "monthly_income", "source_of_income", "is_maya_user", "maya_email",
            "government_id_upload", "bank_statement_upload", "consent"
        ]
    }
    
    return {
        "bank_id": bank_id,
        "name": "Maya Personal Loan",
        "form_type": "personal_loan",
        "version": "1.0",
        "description": "Apply for a fast and convenient personal loan through Maya",
        "schema_json": schema,
        "fields": fields,
        "ui_schema": ui_schema,
        "active": True,
        "created_by": "system"
    }


# ============================================================================
# Security Bank KYC Template (13 fields)
# ============================================================================
def create_security_bank_kyc_template(bank_id: int):
    """Security Bank Know Your Customer (KYC) Form with PEP declaration logic"""
    
    fields = [
        {
            "id": "client_name",
            "type": "text",
            "label": "Full Legal Name",
            "required": True,
            "validation": {"minLength": 5}
        },
        {
            "id": "date_of_birth",
            "type": "date",
            "label": "Date of Birth",
            "required": True
        },
        {
            "id": "place_of_birth",
            "type": "text",
            "label": "Place of Birth",
            "required": True
        },
        {
            "id": "nationality",
            "type": "select",
            "label": "Nationality",
            "required": True,
            "options": ["Filipino", "American", "Chinese", "Japanese", "Korean", "Indian", "Other"]
        },
        {
            "id": "civil_status",
            "type": "select",
            "label": "Civil Status",
            "required": True,
            "options": ["Single", "Married", "Divorced", "Widowed", "Legally Separated"]
        },
        {
            "id": "gender",
            "type": "select",
            "label": "Gender",
            "required": True,
            "options": ["Male", "Female", "Prefer not to say"]
        },
        {
            "id": "tax_id",
            "type": "text",
            "label": "TIN (Tax Identification Number)",
            "required": True,
            "validation": {"pattern": "^\\d{12}$"},
            "placeholder": "12-digit TIN"
        },
        {
            "id": "present_address",
            "type": "textarea",
            "label": "Present Address",
            "required": True,
            "rows": 3
        },
        {
            "id": "permanent_address",
            "type": "textarea",
            "label": "Permanent Address",
            "required": True,
            "rows": 3
        },
        {
            "id": "source_of_funds",
            "type": "select",
            "label": "Primary Source of Funds",
            "required": True,
            "options": ["Employment/Salary", "Business Income", "Investment Returns", "Remittances", "Inheritance", "Savings", "Other"]
        },
        {
            "id": "is_pep",
            "type": "checkbox",
            "label": "I am a Politically Exposed Person (PEP)",
            "required": False,
            "description": "Includes current or former public officials, their family members, and close associates"
        },
        {
            "id": "pep_details",
            "type": "textarea",
            "label": "PEP Details",
            "required": False,
            "rows": 3,
            "show_if": {
                "field": "is_pep",
                "operator": "equals",
                "value": True
            },
            "placeholder": "Please specify your position, office, and relationship"
        },
        {
            "id": "valid_id_upload",
            "type": "file",
            "label": "Valid Government ID",
            "required": True,
            "accept": "image/*,.pdf",
            "max_size_mb": 5
        },
        {
            "id": "proof_of_address",
            "type": "file",
            "label": "Proof of Address (utility bill or bank statement)",
            "required": True,
            "accept": "image/*,.pdf",
            "max_size_mb": 5
        },
        {
            "id": "signature",
            "type": "file",
            "label": "Signature Specimen",
            "required": True,
            "accept": "image/*",
            "max_size_mb": 2,
            "description": "Upload a clear image of your signature on white background"
        },
        {
            "id": "declaration",
            "type": "checkbox",
            "label": "I declare that the information provided is true, complete, and accurate",
            "required": True
        }
    ]
    
    schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "title": "Security Bank KYC Form",
        "properties": {
            "client_name": {"type": "string", "minLength": 5},
            "date_of_birth": {"type": "string", "format": "date"},
            "place_of_birth": {"type": "string"},
            "nationality": {"type": "string", "enum": ["Filipino", "American", "Chinese", "Japanese", "Korean", "Indian", "Other"]},
            "civil_status": {"type": "string", "enum": ["Single", "Married", "Divorced", "Widowed", "Legally Separated"]},
            "gender": {"type": "string", "enum": ["Male", "Female", "Prefer not to say"]},
            "tax_id": {"type": "string", "pattern": "^\\d{12}$"},
            "present_address": {"type": "string"},
            "permanent_address": {"type": "string"},
            "source_of_funds": {"type": "string", "enum": ["Employment/Salary", "Business Income", "Investment Returns", "Remittances", "Inheritance", "Savings", "Other"]},
            "is_pep": {"type": "boolean"},
            "pep_details": {"type": "string"},
            "valid_id_upload": {"type": "string"},
            "proof_of_address": {"type": "string"},
            "signature": {"type": "string"},
            "declaration": {"type": "boolean"}
        },
        "required": [
            "client_name", "date_of_birth", "place_of_birth", "nationality",
            "civil_status", "gender", "tax_id", "present_address",
            "permanent_address", "source_of_funds", "valid_id_upload",
            "proof_of_address", "signature", "declaration"
        ],
        "allOf": [
            {
                "if": {"properties": {"is_pep": {"const": True}}},
                "then": {"required": ["pep_details"]}
            }
        ]
    }
    
    ui_schema = {
        "ui:order": [
            "client_name", "date_of_birth", "place_of_birth", "nationality",
            "civil_status", "gender", "tax_id", "present_address",
            "permanent_address", "source_of_funds", "is_pep", "pep_details",
            "valid_id_upload", "proof_of_address", "signature", "declaration"
        ]
    }
    
    return {
        "bank_id": bank_id,
        "name": "Security Bank KYC Form",
        "form_type": "kyc",
        "version": "1.0",
        "description": "Know Your Customer (KYC) form for Security Bank account opening",
        "schema_json": schema,
        "fields": fields,
        "ui_schema": ui_schema,
        "active": True,
        "created_by": "system"
    }


# ============================================================================
# Seed Database
# ============================================================================
async def seed_data():
    """Main seed function to create banks and templates"""
    print("🌱 Starting database seed...")
    
    # Reset database tables
    try:
        async with engine.begin() as conn:
            print("⚠️ Dropping old form tables...")
            await conn.execute(text("DROP TABLE IF EXISTS form_files CASCADE"))
            await conn.execute(text("DROP TABLE IF EXISTS form_submissions CASCADE"))
            await conn.execute(text("DROP TABLE IF EXISTS form_templates CASCADE"))
            await conn.execute(text("DROP TABLE IF EXISTS banks CASCADE"))
            
            print("🏗️ Recreating tables...")
            await conn.run_sync(Base.metadata.create_all)
    except Exception as e:
        print(f"Error resetting tables: {e}")
        return

    async with AsyncSessionLocal() as session:
        # Create Banks
        banks_data = [
            {"name": "BDO Unibank", "code": "BDO", "primary_color": "#ec1c24", "description": "Banco de Oro - We Find Ways"},
            {"name": "Maya Bank", "code": "MAYA", "primary_color": "#00d26a", "description": "Maya - It's everything and a bank"},
            {"name": "Security Bank", "code": "SECB", "primary_color": "#004a99", "description": "Security Bank - You deserve better"},
        ]
        
        created_banks = {}
        
        print("\n🏦 Creating Banks:")
        for data in banks_data:
            result = await session.execute(select(Bank).where(Bank.code == data["code"]))
            existing = result.scalar_one_or_none()
            
            if existing:
                print(f"   - {data['name']} (Already exists)")
                created_banks[data["code"]] = existing
            else:
                bank = Bank(**data)
                session.add(bank)
                await session.flush()
                print(f"   + {data['name']} (Created)")
                created_banks[data["code"]] = bank
        
        # Create Templates
        print("\n📝 Creating Form Templates:")
        
        if "BDO" in created_banks:
            bdo_template_data = create_bdo_credit_card_template(created_banks["BDO"].id)
            result = await session.execute(
                select(FormTemplate).where(
                    FormTemplate.bank_id == created_banks["BDO"].id,
                    FormTemplate.name == bdo_template_data["name"]
                )
            )
            if not result.scalar_one_or_none():
                template = FormTemplate(**bdo_template_data)
                session.add(template)
                print(f"   + BDO Credit Card Application (15 fields)")
            else:
                print(f"   - BDO Credit Card Application (Already exists)")
        
        if "MAYA" in created_banks:
            maya_template_data = create_maya_personal_loan_template(created_banks["MAYA"].id)
            result = await session.execute(
                select(FormTemplate).where(
                    FormTemplate.bank_id == created_banks["MAYA"].id,
                    FormTemplate.name == maya_template_data["name"]
                )
            )
            if not result.scalar_one_or_none():
                template = FormTemplate(**maya_template_data)
                session.add(template)
                print(f"   + Maya Personal Loan (14 fields)")
            else:
                print(f"   - Maya Personal Loan (Already exists)")
        
        if "SECB" in created_banks:
            secb_template_data = create_security_bank_kyc_template(created_banks["SECB"].id)
            result = await session.execute(
                select(FormTemplate).where(
                    FormTemplate.bank_id == created_banks["SECB"].id,
                    FormTemplate.name == secb_template_data["name"]
                )
            )
            if not result.scalar_one_or_none():
                template = FormTemplate(**secb_template_data)
                session.add(template)
                print(f"   + Security Bank KYC Form (16 fields)")
            else:
                print(f"   - Security Bank KYC Form (Already exists)")
        
        await session.commit()
        print("\n✅ Seed completed successfully!")
        print("\n📋 Template Summary:")
        print("   BDO: Credit Card Application (15 fields, conditional logic, file uploads)")
        print("   Maya: Personal Loan (14 fields, all/any operators, file uploads)")
        print("   SECB: KYC Form (16 fields, PEP logic, comprehensive validation)")
        
        # Seed ABAC and ReBAC policies
        print("\n🔐 Seeding ABAC & ReBAC Policies...")
        try:
            await seed_abac_policies(session)
            await seed_user_attributes(session)
            await seed_resource_attributes(session)
            await seed_rebac_relationships(session)
            print("✅ ABAC & ReBAC policies seeded successfully!")
        except Exception as e:
            print(f"⚠️  Warning: ABAC/ReBAC seeding failed: {str(e)}")
            import traceback
            traceback.print_exc()
        
        # Ensure permissions are synced to Casbin and DB
        print("\n🔐 Syncing permissions to Casbin...")
        from scripts.ensure_permissions import ensure_permissions
        try:
            await ensure_permissions()
            print("✅ Permissions synced successfully!")
        except Exception as e:
            print(f"⚠️  Warning: Permission sync failed: {str(e)}")


# ============================================================================
# ABAC & ReBAC Seed Functions
# ============================================================================

async def seed_abac_policies(db):
    """Seed realistic ABAC policies"""
    print("   🔐 Seeding ABAC Policies...")
    
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
                    {"field": "user.user_role", "operator": "==", "value": "admin"}
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
                    {"field": "user.user_role", "operator": "==", "value": "supervisor"}
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
        },
        {
            "name": "Department-Based Access",
            "description": "Users can access resources from their department",
            "rules": {
                "condition": "all",
                "rules": [
                    {"field": "user.department", "operator": "==", "value": "resource.department"}
                ]
            },
            "is_active": True
        }
    ]
    
    for policy_data in policies:
        db.add(ABACPolicy(**policy_data))
    
    await db.commit()
    print(f"      ✅ Created {len(policies)} ABAC policies")


async def seed_user_attributes(db):
    """Seed user attributes from real users"""
    print("   👤 Seeding User Attributes...")
    
    # Delete existing
    await db.execute(text("DELETE FROM user_attributes"))
    await db.commit()
    
    # Get real users
    result = await db.execute(select(User).limit(50))
    users = result.scalars().all()
    
    if not users:
        print("      ⚠️  No users found. Skipping...")
        return
    
    attributes_data = []
    
    for user in users:
        # Department attribute
        if user.department:
            attributes_data.append({
                "user_id": user.id,
                "attribute_key": "department",
                "attribute_value": user.department
            })
        
        # Level attribute
        if user.level:
            attributes_data.append({
                "user_id": user.id,
                "attribute_key": "level",
                "attribute_value": str(user.level)
            })
        
        # Location attribute
        if user.location:
            attributes_data.append({
                "user_id": user.id,
                "attribute_key": "location",
                "attribute_value": user.location
            })
        
        # Role-based attributes
        if user.user_role:
            clearance_map = {
                "admin": "full",
                "supervisor": "high",
                "moderator": "medium",
                "user": "standard"
            }
            attributes_data.append({
                "user_id": user.id,
                "attribute_key": "clearance",
                "attribute_value": clearance_map.get(user.user_role, "standard")
            })
    
    for attr_data in attributes_data:
        db.add(UserAttribute(**attr_data))
    
    await db.commit()
    print(f"      ✅ Created {len(attributes_data)} user attributes")


async def seed_resource_attributes(db):
    """Seed resource attributes for templates and submissions"""
    print("   📦 Seeding Resource Attributes...")
    
    # Delete existing
    await db.execute(text("DELETE FROM resource_attributes"))
    await db.commit()
    
    # Get templates
    templates_result = await db.execute(select(FormTemplate).limit(10))
    templates = templates_result.scalars().all()
    
    # Get submissions
    submissions_result = await db.execute(select(FormSubmission).limit(10))
    submissions = submissions_result.scalars().all()
    
    attributes_data = []
    
    # Add attributes to templates
    for i, template in enumerate(templates):
        classification = "public" if i % 2 == 0 else "confidential"
        attributes_data.extend([
            {"resource_type": "template", "resource_id": str(template.id), 
             "attribute_key": "classification", "attribute_value": classification},
            {"resource_type": "template", "resource_id": str(template.id), 
             "attribute_key": "bank_id", "attribute_value": str(template.bank_id)},
            {"resource_type": "template", "resource_id": str(template.id), 
             "attribute_key": "form_type", "attribute_value": template.form_type or "general"}
        ])
    
    # Add attributes to submissions
    for submission in submissions:
        attributes_data.extend([
            {"resource_type": "submission", "resource_id": str(submission.id),
             "attribute_key": "user_id", "attribute_value": str(submission.user_id)},
            {"resource_type": "submission", "resource_id": str(submission.id),
             "attribute_key": "status", "attribute_value": submission.status},
            {"resource_type": "submission", "resource_id": str(submission.id),
             "attribute_key": "template_id", "attribute_value": str(submission.template_id)}
        ])
    
    for attr_data in attributes_data:
        db.add(ResourceAttribute(**attr_data))
    
    await db.commit()
    print(f"      ✅ Created {len(attributes_data)} resource attributes")


async def seed_rebac_relationships(db):
    """Seed ReBAC relationships with graph-traversable connections"""
    print("   🔗 Seeding ReBAC Relationships...")
    
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
    
    roles_result = await db.execute(select(Role).limit(5))
    roles = roles_result.scalars().all()
    
    if not users:
        print("      ⚠️  No users found. Skipping...")
        return
    
    relationships_data = []
    
    # === User -> Template Relationships (Ownership & Viewing) ===
    for i, template in enumerate(templates[:3]):
        if i < len(users):
            # Owner relationship
            relationships_data.append({
                "subject_type": "user",
                "subject_id": str(users[i].id),
                "relationship_type": "owner",
                "resource_type": "template",
                "resource_id": str(template.id),
                "parent_resource_type": "bank",
                "parent_resource_id": str(template.bank_id)
            })
            
            # Editor relationship for next user
            if i + 1 < len(users):
                relationships_data.append({
                    "subject_type": "user",
                    "subject_id": str(users[i + 1].id),
                    "relationship_type": "editor",
                    "resource_type": "template",
                    "resource_id": str(template.id),
                    "parent_resource_type": "bank",
                    "parent_resource_id": str(template.bank_id)
                })
    
    # Viewer relationships for all users on all templates
    for template in templates:
        for j in range(min(3, len(users))):
            relationships_data.append({
                "subject_type": "user",
                "subject_id": str(users[j].id),
                "relationship_type": "viewer",
                "resource_type": "template",
                "resource_id": str(template.id),
                "parent_resource_type": "bank",
                "parent_resource_id": str(template.bank_id)
            })
    
    # === User -> Submission Relationships (Ownership & Management) ===
    for submission in submissions:
        # Owner relationship (the user who submitted)
        relationships_data.append({
            "subject_type": "user",
            "subject_id": str(submission.user_id),
            "relationship_type": "owner",
            "resource_type": "submission",
            "resource_id": str(submission.id),
            "parent_resource_type": "template",
            "parent_resource_id": str(submission.template_id)
        })
        
        # Reviewer relationship (different user)
        reviewer_user = next((u for u in users if u.id != submission.user_id), None)
        if reviewer_user:
            relationships_data.append({
                "subject_type": "user",
                "subject_id": str(reviewer_user.id),
                "relationship_type": "reviewer",
                "resource_type": "submission",
                "resource_id": str(submission.id),
                "parent_resource_type": "template",
                "parent_resource_id": str(submission.template_id)
            })
    
    # === Role -> Template Relationships (Administrative Access) ===
    admin_users = [u for u in users if u.user_role == 'admin']
    manager_users = [u for u in users if u.user_role == 'manager']
    
    if admin_users and templates:
        # Admin role can manage all templates
        for template in templates[:2]:
            relationships_data.append({
                "subject_type": "role",
                "subject_id": "admin",
                "relationship_type": "manager",
                "resource_type": "template",
                "resource_id": str(template.id),
                "parent_resource_type": "bank",
                "parent_resource_id": str(template.bank_id)
            })
    
    if manager_users and templates:
        # Manager role can manage specific templates
        relationships_data.append({
            "subject_type": "role",
            "subject_id": "manager",
            "relationship_type": "manager",
            "resource_type": "template",
            "resource_id": str(templates[0].id),
            "parent_resource_type": "bank",
            "parent_resource_id": str(templates[0].bank_id)
        })
    
    # === User -> Role Relationships (Role Membership) ===
    if roles and users:
        for i, role in enumerate(roles[:3]):
            if i < len(users):
                relationships_data.append({
                    "subject_type": "user",
                    "subject_id": str(users[i].id),
                    "relationship_type": "member",
                    "resource_type": "role",
                    "resource_id": str(role.id),
                    "parent_resource_type": "",  # Empty string instead of None
                    "parent_resource_id": ""  # Empty string instead of None
                })
    
    # === Template -> Template Relationships (Template Hierarchy) ===
    if len(templates) >= 2:
        # Parent template relationship
        relationships_data.append({
            "subject_type": "template",
            "subject_id": str(templates[0].id),
            "relationship_type": "parent",
            "resource_type": "template",
            "resource_id": str(templates[1].id),
            "parent_resource_type": "bank",
            "parent_resource_id": str(templates[0].bank_id)
        })
    
    # === Submission -> Submission Relationships (Linked Submissions) ===
    if len(submissions) >= 2:
        # Related submissions (for approval workflow)
        relationships_data.append({
            "subject_type": "submission",
            "subject_id": str(submissions[0].id),
            "relationship_type": "depends_on",
            "resource_type": "submission",
            "resource_id": str(submissions[1].id),
            "parent_resource_type": "template",
            "parent_resource_id": str(submissions[0].template_id)
        })
    
    # === User -> User Relationships (Delegation & Reporting) ===
    if len(users) >= 3:
        # Manager delegates to user
        relationships_data.append({
            "subject_type": "user",
            "subject_id": str(users[0].id),
            "relationship_type": "delegate",
            "resource_type": "user",
            "resource_id": str(users[1].id),
            "parent_resource_type": "",  # Empty string instead of None
            "parent_resource_id": ""  # Empty string instead of None
        })
        
        # User reports to manager
        relationships_data.append({
            "subject_type": "user",
            "subject_id": str(users[2].id),
            "relationship_type": "reports_to",
            "resource_type": "user",
            "resource_id": str(users[0].id),
            "parent_resource_type": "",  # Empty string instead of None
            "parent_resource_id": ""  # Empty string instead of None
        })
    
    for rel_data in relationships_data:
        db.add(ResourceRelationship(**rel_data))
    
    await db.commit()
    print(f"      ✅ Created {len(relationships_data)} ReBAC relationships (graph-traversable)")



if __name__ == "__main__":
    asyncio.run(seed_data())

