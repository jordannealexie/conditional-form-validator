"""
Seed script for field types and enum definitions
Populates commonly used enums and custom field types
"""
import asyncio
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import AsyncSessionLocal
from app.services.field_types import EnumDefinitionService, FieldTypeDefinitionService
from app.schemas.field_types import EnumDefinitionCreate, FieldTypeDefinitionCreate


async def seed_common_enums(db: AsyncSession):
    """Seed commonly used enum definitions"""
    enum_service = EnumDefinitionService(db)
    
    enums_to_create = [
        # Marital Status
        {
            "name": "marital_status",
            "display_name": "Marital Status",
            "description": "Common marital status options",
            "source_type": "static",
            "static_options": [
                {"value": "single", "label": "Single"},
                {"value": "married", "label": "Married"},
                {"value": "divorced", "label": "Divorced"},
                {"value": "widowed", "label": "Widowed"},
                {"value": "separated", "label": "Separated"}
            ],
            "created_by": "system"
        },
        
        # Gender
        {
            "name": "gender",
            "display_name": "Gender",
            "description": "Gender options",
            "source_type": "static",
            "static_options": [
                {"value": "male", "label": "Male"},
                {"value": "female", "label": "Female"},
                {"value": "other", "label": "Other"},
                {"value": "prefer_not_to_say", "label": "Prefer not to say"}
            ],
            "created_by": "system"
        },
        
        # Employment Status
        {
            "name": "employment_status",
            "display_name": "Employment Status",
            "description": "Employment status options",
            "source_type": "static",
            "static_options": [
                {"value": "employed", "label": "Employed"},
                {"value": "self_employed", "label": "Self-Employed"},
                {"value": "unemployed", "label": "Unemployed"},
                {"value": "student", "label": "Student"},
                {"value": "retired", "label": "Retired"}
            ],
            "created_by": "system"
        },
        
        # Education Level
        {
            "name": "education_level",
            "display_name": "Education Level",
            "description": "Educational attainment options",
            "source_type": "static",
            "static_options": [
                {"value": "elementary", "label": "Elementary"},
                {"value": "high_school", "label": "High School"},
                {"value": "vocational", "label": "Vocational"},
                {"value": "college", "label": "College/University"},
                {"value": "graduate", "label": "Graduate Degree"}
            ],
            "created_by": "system"
        },
        
        # Relationship Types
        {
            "name": "relationship_type",
            "display_name": "Relationship",
            "description": "Family relationship types",
            "source_type": "static",
            "static_options": [
                {"value": "spouse", "label": "Spouse"},
                {"value": "child", "label": "Child"},
                {"value": "parent", "label": "Parent"},
                {"value": "sibling", "label": "Sibling"},
                {"value": "other", "label": "Other"}
            ],
            "created_by": "system"
        },
        
        # Loan Purpose
        {
            "name": "loan_purpose",
            "display_name": "Loan Purpose",
            "description": "Common loan purposes",
            "source_type": "static",
            "static_options": [
                {"value": "business", "label": "Business"},
                {"value": "education", "label": "Education"},
                {"value": "medical", "label": "Medical"},
                {"value": "home_improvement", "label": "Home Improvement"},
                {"value": "debt_consolidation", "label": "Debt Consolidation"},
                {"value": "personal", "label": "Personal"}
            ],
            "created_by": "system"
        },
        
        # Yes/No Options
        {
            "name": "yes_no",
            "display_name": "Yes/No",
            "description": "Simple yes/no options",
            "source_type": "static",
            "static_options": [
                {"value": "yes", "label": "Yes"},
                {"value": "no", "label": "No"}
            ],
            "created_by": "system"
        },
        
        # Philippine Regions
        {
            "name": "ph_regions",
            "display_name": "Philippine Regions",
            "description": "Philippine regions",
            "source_type": "static",
            "static_options": [
                {"value": "ncr", "label": "National Capital Region (NCR)"},
                {"value": "car", "label": "Cordillera Administrative Region (CAR)"},
                {"value": "region1", "label": "Region I (Ilocos Region)"},
                {"value": "region2", "label": "Region II (Cagayan Valley)"},
                {"value": "region3", "label": "Region III (Central Luzon)"},
                {"value": "region4a", "label": "Region IV-A (CALABARZON)"},
                {"value": "region4b", "label": "Region IV-B (MIMAROPA)"},
                {"value": "region5", "label": "Region V (Bicol Region)"},
                {"value": "region6", "label": "Region VI (Western Visayas)"},
                {"value": "region7", "label": "Region VII (Central Visayas)"},
                {"value": "region8", "label": "Region VIII (Eastern Visayas)"},
                {"value": "region9", "label": "Region IX (Zamboanga Peninsula)"},
                {"value": "region10", "label": "Region X (Northern Mindanao)"},
                {"value": "region11", "label": "Region XI (Davao Region)"},
                {"value": "region12", "label": "Region XII (SOCCSKSARGEN)"},
                {"value": "region13", "label": "Region XIII (Caraga)"},
                {"value": "barmm", "label": "BARMM (Bangsamoro)"}
            ],
            "created_by": "system"
        }
    ]
    
    created_count = 0
    for enum_data in enums_to_create:
        try:
            # Check if already exists
            existing = await enum_service.repo.get_by_name(db, enum_data["name"])
            if existing:
                print(f"  ⏭️  Enum '{enum_data['name']}' already exists")
                continue
            
            enum_create = EnumDefinitionCreate(**enum_data)
            await enum_service.create_enum(enum_create)
            print(f"  ✅ Created enum: {enum_data['name']}")
            created_count += 1
        except Exception as e:
            print(f"  ❌ Error creating enum '{enum_data['name']}': {e}")
    
    return created_count


async def seed_custom_field_types(db: AsyncSession):
    """Seed custom field type definitions"""
    field_type_service = FieldTypeDefinitionService(db)
    
    field_types_to_create = [
        # Philippine Mobile Number
        {
            "name": "ph_mobile_number",
            "display_name": "Philippine Mobile Number",
            "description": "Philippine mobile number with +63 prefix",
            "base_type": "phone",
            "schema_definition": {
                "type": "string",
                "pattern": r"^\+639\d{9}$",
                "description": "Format: +639XXXXXXXXX"
            },
            "ui_widget": "tel",
            "validation_rules": {
                "pattern": r"^\+639\d{9}$"
            },
            "created_by": "system"
        },
        
        # Philippine Tax ID (TIN)
        {
            "name": "ph_tin",
            "display_name": "Philippine TIN",
            "description": "Philippine Tax Identification Number",
            "base_type": "text",
            "schema_definition": {
                "type": "string",
                "pattern": r"^\d{3}-\d{3}-\d{3}-\d{3}$",
                "description": "Format: XXX-XXX-XXX-XXX"
            },
            "ui_widget": "text",
            "validation_rules": {
                "pattern": r"^\d{3}-\d{3}-\d{3}-\d{3}$"
            },
            "created_by": "system"
        },
        
        # Philippine SSS Number
        {
            "name": "ph_sss_number",
            "display_name": "Philippine SSS Number",
            "description": "Philippine Social Security System number",
            "base_type": "text",
            "schema_definition": {
                "type": "string",
                "pattern": r"^\d{2}-\d{7}-\d{1}$",
                "description": "Format: XX-XXXXXXX-X"
            },
            "ui_widget": "text",
            "validation_rules": {
                "pattern": r"^\d{2}-\d{7}-\d{1}$"
            },
            "created_by": "system"
        },
        
        # Credit Card Number (masked)
        {
            "name": "credit_card_number",
            "display_name": "Credit Card Number",
            "description": "Credit card number (16 digits)",
            "base_type": "text",
            "schema_definition": {
                "type": "string",
                "pattern": r"^\d{16}$",
                "minLength": 16,
                "maxLength": 16
            },
            "ui_widget": "text",
            "ui_options": {
                "inputType": "password",
                "mask": "####-####-####-####"
            },
            "validation_rules": {
                "pattern": r"^\d{16}$"
            },
            "created_by": "system"
        },
        
        # Full Name (with validation)
        {
            "name": "full_name",
            "display_name": "Full Name",
            "description": "Complete name with proper validation",
            "base_type": "text",
            "schema_definition": {
                "type": "string",
                "minLength": 2,
                "maxLength": 100,
                "pattern": r"^[a-zA-Z\s\-\.]+$"
            },
            "ui_widget": "text",
            "validation_rules": {
                "minLength": 2,
                "maxLength": 100,
                "pattern": r"^[a-zA-Z\s\-\.]+$"
            },
            "created_by": "system"
        },
        
        # Age (18-100)
        {
            "name": "adult_age",
            "display_name": "Adult Age",
            "description": "Age for adults only (18-100)",
            "base_type": "integer",
            "schema_definition": {
                "type": "integer",
                "minimum": 18,
                "maximum": 100
            },
            "ui_widget": "updown",
            "validation_rules": {
                "minimum": 18,
                "maximum": 100
            },
            "created_by": "system"
        },
        
        # Salary Range
        {
            "name": "monthly_salary",
            "display_name": "Monthly Salary (PHP)",
            "description": "Monthly salary in Philippine Peso",
            "base_type": "currency",
            "schema_definition": {
                "type": "number",
                "minimum": 0,
                "maximum": 10000000,
                "multipleOf": 0.01
            },
            "ui_widget": "currency",
            "ui_options": {
                "currency": "PHP",
                "locale": "en-PH"
            },
            "validation_rules": {
                "minimum": 0,
                "maximum": 10000000
            },
            "created_by": "system"
        }
    ]
    
    created_count = 0
    for field_type_data in field_types_to_create:
        try:
            # Check if already exists
            existing = await field_type_service.repo.get_by_name(db, field_type_data["name"])
            if existing:
                print(f"  ⏭️  Field type '{field_type_data['name']}' already exists")
                continue
            
            field_type_create = FieldTypeDefinitionCreate(**field_type_data)
            await field_type_service.create_field_type(field_type_create)
            print(f"  ✅ Created field type: {field_type_data['name']}")
            created_count += 1
        except Exception as e:
            print(f"  ❌ Error creating field type '{field_type_data['name']}': {e}")
    
    return created_count


async def main():
    """Main seeding function"""
    print("🌱 Seeding Field Types and Enum Definitions...")
    print()
    
    async with AsyncSessionLocal() as db:
        try:
            # Seed enums
            print("📊 Seeding Enum Definitions...")
            enum_count = await seed_common_enums(db)
            print(f"   Created {enum_count} new enum definitions")
            print()
            
            # Seed field types
            print("📝 Seeding Custom Field Types...")
            field_type_count = await seed_custom_field_types(db)
            print(f"   Created {field_type_count} new field type definitions")
            print()
            
            print("✨ Seeding completed successfully!")
            print(f"   Total enums created: {enum_count}")
            print(f"   Total field types created: {field_type_count}")
            
        except Exception as e:
            print(f"❌ Error during seeding: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(main())
