"""
Seed predefined field types with comprehensive validation rules
Run: python backend/scripts/seed_predefined_field_types.py
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.session import AsyncSessionLocal
from app.repositories.field_types import FieldTypeDefinitionRepository


PREDEFINED_FIELD_TYPES = [
    {
        "name": "text",
        "display_name": "Text Field",
        "description": "Single-line text input",
        "base_type": "string",
        "schema_definition": {
            "type": "string",
            "maxLength": 255
        },
        "validation_rules": {
            "type": "string",
            "not": {"type": ["number", "integer", "boolean", "array", "object"]}
        },
        "strict_type_checking": True,
        "ui_widget": "text",
        "active": True
    },
    {
        "name": "long_text",
        "display_name": "Long Text / Textarea",
        "description": "Multi-line text input",
        "base_type": "string",
        "schema_definition": {
            "type": "string",
            "maxLength": 5000
        },
        "validation_rules": {
            "type": "string",
            "not": {"type": ["number", "integer", "boolean", "array", "object"]}
        },
        "strict_type_checking": True,
        "ui_widget": "textarea",
        "active": True
    },
    {
        "name": "email",
        "display_name": "Email",
        "description": "Email address with validation",
        "base_type": "string",
        "schema_definition": {
            "type": "string",
            "format": "email",
            "maxLength": 255
        },
        "validation_rules": {
            "type": "string",
            "format": "email",
            "not": {"type": ["number", "integer", "boolean", "array", "object"]}
        },
        "strict_type_checking": True,
        "ui_widget": "email",
        "active": True
    },
    {
        "name": "phone",
        "display_name": "Phone Number",
        "description": "Phone number (string format)",
        "base_type": "string",
        "schema_definition": {
            "type": "string",
            "pattern": "^[+]?[(]?[0-9]{1,4}[)]?[-\\s\\.]?[(]?[0-9]{1,4}[)]?[-\\s\\.]?[0-9]{1,9}$",
            "maxLength": 20
        },
        "validation_rules": {
            "type": "string",
            "not": {"type": ["number", "integer", "boolean", "array", "object"]}
        },
        "strict_type_checking": True,
        "ui_widget": "tel",
        "active": True
    },
    {
        "name": "password",
        "display_name": "Password",
        "description": "Password input (hidden)",
        "base_type": "string",
        "schema_definition": {
            "type": "string",
            "minLength": 8,
            "maxLength": 100
        },
        "validation_rules": {
            "type": "string",
            "not": {"type": ["number", "integer", "boolean", "array", "object"]}
        },
        "strict_type_checking": True,
        "ui_widget": "password",
        "active": True
    },
    {
        "name": "number",
        "display_name": "Number Field (Generic)",
        "description": "Any numeric value (int or float)",
        "base_type": "number",
        "schema_definition": {
            "type": "number"
        },
        "validation_rules": {
            "type": "number",
            "not": {"type": ["string", "boolean", "array", "object"]}
        },
        "strict_type_checking": True,
        "ui_widget": "number",
        "active": True
    },
    {
        "name": "integer",
        "display_name": "Integer Field",
        "description": "Whole numbers only (no decimals)",
        "base_type": "integer",
        "schema_definition": {
            "type": "integer"
        },
        "validation_rules": {
            "type": "integer",
            "not": {"type": ["string", "boolean", "array", "object"]}
        },
        "strict_type_checking": True,
        "ui_widget": "number",
        "active": True
    },
    {
        "name": "currency",
        "display_name": "Currency",
        "description": "Monetary value",
        "base_type": "number",
        "schema_definition": {
            "type": "number",
            "minimum": 0,
            "multipleOf": 0.01
        },
        "validation_rules": {
            "type": "number",
            "not": {"type": ["string", "boolean", "array", "object"]}
        },
        "strict_type_checking": True,
        "ui_widget": "currency",
        "ui_options": {"currency": "PHP", "locale": "en-PH"},
        "active": True
    },
    {
        "name": "percentage",
        "display_name": "Percentage",
        "description": "Percentage value (0-100)",
        "base_type": "number",
        "schema_definition": {
            "type": "number",
            "minimum": 0,
            "maximum": 100
        },
        "validation_rules": {
            "type": "number",
            "not": {"type": ["string", "boolean", "array", "object"]}
        },
        "strict_type_checking": True,
        "ui_widget": "percentage",
        "active": True
    },
    {
        "name": "date",
        "display_name": "Date Field",
        "description": "Date selector (YYYY-MM-DD)",
        "base_type": "string",
        "schema_definition": {
            "type": "string",
            "format": "date"
        },
        "validation_rules": {
            "type": "string",
            "format": "date",
            "not": {"type": ["number", "integer", "boolean", "array", "object"]}
        },
        "strict_type_checking": True,
        "ui_widget": "date",
        "active": True
    },
    {
        "name": "boolean",
        "display_name": "Boolean / Checkbox",
        "description": "True/False value",
        "base_type": "boolean",
        "schema_definition": {
            "type": "boolean"
        },
        "validation_rules": {
            "type": "boolean",
            "not": {"type": ["string", "number", "integer", "array", "object"]}
        },
        "strict_type_checking": True,
        "ui_widget": "checkbox",
        "active": True
    },
    {
        "name": "enum",
        "display_name": "Enum Field / Dropdown",
        "description": "Select from predefined options",
        "base_type": "string",
        "schema_definition": {
            "type": "string",
            "enum": []  # Will be populated per field
        },
        "validation_rules": {
            "type": "string",
            "not": {"type": ["number", "integer", "boolean", "array", "object"]}
        },
        "strict_type_checking": True,
        "ui_widget": "select",
        "active": True
    },
    {
        "name": "file",
        "display_name": "File Upload",
        "description": "File upload field (returns token/URL)",
        "base_type": "string",
        "schema_definition": {
            "type": "string",
            "format": "uri"
        },
        "validation_rules": {
            "type": "string",
            "not": {"type": ["number", "integer", "boolean", "array", "object"]}
        },
        "strict_type_checking": True,
        "ui_widget": "file",
        "active": True
    },
    {
        "name": "rating",
        "display_name": "Rating",
        "description": "Star rating or numeric score",
        "base_type": "integer",
        "schema_definition": {
            "type": "integer",
            "minimum": 1,
            "maximum": 5
        },
        "validation_rules": {
            "type": "integer",
            "not": {"type": ["string", "boolean", "array", "object"]}
        },
        "strict_type_checking": True,
        "ui_widget": "rating",
        "active": True
    },
    {
        "name": "url",
        "display_name": "URL Field",
        "description": "Web address with validation",
        "base_type": "string",
        "schema_definition": {
            "type": "string",
            "format": "uri",
            "maxLength": 500
        },
        "validation_rules": {
            "type": "string",
            "format": "uri",
            "not": {"type": ["number", "integer", "boolean", "array", "object"]}
        },
        "strict_type_checking": True,
        "ui_widget": "url",
        "active": True
    },
    {
        "name": "json",
        "display_name": "JSON Field",
        "description": "Arbitrary JSON data",
        "base_type": "object",
        "schema_definition": {
            "type": "object"
        },
        "validation_rules": {
            "type": "object",
            "not": {"type": ["string", "number", "integer", "boolean", "array"]}
        },
        "strict_type_checking": True,
        "ui_widget": "json",
        "active": True
    },
    {
        "name": "address",
        "display_name": "Address (Structured)",
        "description": "Philippine address with structured fields",
        "base_type": "object",
        "schema_definition": {
            "type": "object",
            "properties": {
                "street": {"type": "string", "maxLength": 255},
                "barangay": {"type": "string", "maxLength": 100},
                "city": {"type": "string", "maxLength": 100},
                "province": {"type": "string", "maxLength": 100},
                "zip_code": {"type": "string", "pattern": "^[0-9]{4}$"}
            },
            "required": ["city", "province"]
        },
        "validation_rules": {
            "type": "object",
            "not": {"type": ["string", "number", "integer", "boolean", "array"]},
            "properties": {
                "street": {
                    "type": "string",
                    "not": {"type": ["number", "integer", "boolean", "array", "object"]}
                },
                "barangay": {
                    "type": "string",
                    "not": {"type": ["number", "integer", "boolean", "array", "object"]}
                },
                "city": {
                    "type": "string",
                    "not": {"type": ["number", "integer", "boolean", "array", "object"]}
                },
                "province": {
                    "type": "string",
                    "not": {"type": ["number", "integer", "boolean", "array", "object"]}
                },
                "zip_code": {
                    "type": "string",
                    "not": {"type": ["number", "integer", "boolean", "array", "object"]}
                }
            }
        },
        "strict_type_checking": True,
        "ui_widget": "address",
        "ui_options": {"country": "Philippines"},
        "active": True
    }
]


async def seed_predefined_types():
    """Seed all predefined field types"""
    print("\n" + "="*70)
    print("🌱 Seeding Predefined Field Types")
    print("="*70)
    
    async with AsyncSessionLocal() as db:
        repo = FieldTypeDefinitionRepository()
        created_count = 0
        updated_count = 0
        
        for field_type_data in PREDEFINED_FIELD_TYPES:
            try:
                # Check if exists
                existing = await repo.get_by_name(db, field_type_data["name"])
                
                if existing:
                    # Update existing
                    updated = await repo.update(db, existing, **field_type_data)
                    print(f"   ✅ Updated: {field_type_data['display_name']}")
                    updated_count += 1
                else:
                    # Create new
                    created_by_user = "system"
                    created = await repo.create(db, created_by=created_by_user, **field_type_data)
                    print(f"   ✨ Created: {field_type_data['display_name']}")
                    created_count += 1
                    
            except Exception as e:
                print(f"   ❌ Error with {field_type_data['name']}: {e}")
        
        print("\n" + "="*70)
        print(f"✨ Seeding Complete!")
        print(f"   Created: {created_count}")
        print(f"   Updated: {updated_count}")
        print("="*70 + "\n")


if __name__ == "__main__":
    asyncio.run(seed_predefined_types())
