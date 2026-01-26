"""
Example usage of the field types and dynamic form system
Demonstrates creating forms using the new system
"""
import asyncio
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import AsyncSessionLocal
from app.services.field_types import FormSchemaGeneratorService
from app.schemas.field_types import FormSchemaBuilder, FieldConfig
import json


async def example_simple_contact_form(db: AsyncSession):
    """Example: Simple contact form"""
    print("\n📝 Example 1: Simple Contact Form")
    print("=" * 60)
    
    schema_generator = FormSchemaGeneratorService(db)
    
    form_builder = FormSchemaBuilder(
        title="Contact Form",
        description="Simple contact form with basic fields",
        fields=[
            FieldConfig(
                name="full_name",
                label="Full Name",
                type="text",
                required=True,
                placeholder="Enter your full name",
                validation={"minLength": 2, "maxLength": 100}
            ),
            FieldConfig(
                name="email",
                label="Email Address",
                type="email",
                required=True,
                placeholder="your.email@example.com"
            ),
            FieldConfig(
                name="phone",
                label="Phone Number",
                type="ph_mobile_number",  # Custom field type
                required=True,
                placeholder="+639171234567"
            ),
            FieldConfig(
                name="message",
                label="Message",
                type="long_text",
                required=True,
                placeholder="Enter your message here...",
                validation={"minLength": 10, "maxLength": 1000}
            )
        ]
    )
    
    result = await schema_generator.generate_schema(form_builder)
    
    print("\nGenerated Schema:")
    print(json.dumps(result["schema_json"], indent=2))


async def example_loan_application(db: AsyncSession):
    """Example: Loan application with conditional fields"""
    print("\n💰 Example 2: Loan Application Form")
    print("=" * 60)
    
    schema_generator = FormSchemaGeneratorService(db)
    
    form_builder = FormSchemaBuilder(
        title="Personal Loan Application",
        description="Apply for a personal loan",
        fields=[
            # Personal Information
            FieldConfig(
                name="full_name",
                label="Full Name",
                type="full_name",
                required=True
            ),
            FieldConfig(
                name="email",
                label="Email Address",
                type="email",
                required=True
            ),
            FieldConfig(
                name="mobile_number",
                label="Mobile Number",
                type="ph_mobile_number",
                required=True
            ),
            FieldConfig(
                name="date_of_birth",
                label="Date of Birth",
                type="date",
                required=True
            ),
            FieldConfig(
                name="age",
                label="Age",
                type="adult_age",
                required=True
            ),
            FieldConfig(
                name="gender",
                label="Gender",
                type="enum",
                required=True,
                enum_definition_id=2  # Assuming gender enum ID is 2
            ),
            FieldConfig(
                name="marital_status",
                label="Marital Status",
                type="enum",
                required=True,
                enum_definition_id=1  # Assuming marital_status enum ID is 1
            ),
            
            # Employment Information
            FieldConfig(
                name="employment_status",
                label="Employment Status",
                type="enum",
                required=True,
                enum_definition_id=3  # Assuming employment_status enum ID is 3
            ),
            FieldConfig(
                name="monthly_income",
                label="Monthly Income",
                type="monthly_salary",
                required=True
            ),
            
            # Loan Details
            FieldConfig(
                name="loan_amount",
                label="Loan Amount",
                type="currency",
                required=True,
                validation={"minimum": 10000, "maximum": 500000}
            ),
            FieldConfig(
                name="loan_purpose",
                label="Loan Purpose",
                type="enum",
                required=True,
                enum_definition_id=6  # Assuming loan_purpose enum ID is 6
            ),
            FieldConfig(
                name="loan_term_months",
                label="Loan Term (Months)",
                type="integer",
                required=True,
                validation={"minimum": 6, "maximum": 60}
            ),
            
            # Address
            FieldConfig(
                name="home_address",
                label="Home Address",
                type="address",
                required=True
            )
        ]
    )
    
    result = await schema_generator.generate_schema(form_builder)
    
    print("\nGenerated Schema Properties:")
    for field_name in result["schema_json"]["properties"].keys():
        print(f"  - {field_name}")
    
    print(f"\nRequired Fields: {len(result['schema_json']['required'])}")
    print(f"Total Fields: {len(result['schema_json']['properties'])}")


async def example_credit_card_application(db: AsyncSession):
    """Example: Credit card application with complex validation"""
    print("\n💳 Example 3: Credit Card Application")
    print("=" * 60)
    
    schema_generator = FormSchemaGeneratorService(db)
    
    form_builder = FormSchemaBuilder(
        title="Credit Card Application",
        description="Apply for a credit card",
        fields=[
            # Personal Information
            FieldConfig(
                name="applicant_name",
                label="Full Name",
                type="full_name",
                required=True
            ),
            FieldConfig(
                name="email",
                label="Email Address",
                type="email",
                required=True
            ),
            FieldConfig(
                name="mobile",
                label="Mobile Number",
                type="ph_mobile_number",
                required=True
            ),
            FieldConfig(
                name="tin",
                label="Tax Identification Number",
                type="ph_tin",
                required=True
            ),
            FieldConfig(
                name="sss_number",
                label="SSS Number",
                type="ph_sss_number",
                required=False
            ),
            
            # Financial Information
            FieldConfig(
                name="annual_income",
                label="Annual Income",
                type="currency",
                required=True,
                validation={"minimum": 120000}  # At least 120k per year
            ),
            FieldConfig(
                name="has_existing_credit_card",
                label="Do you have an existing credit card?",
                type="boolean",
                required=True
            ),
            
            # Address
            FieldConfig(
                name="mailing_address",
                label="Mailing Address",
                type="address",
                required=True
            ),
            
            # References
            FieldConfig(
                name="references",
                label="Personal References",
                type="array",
                items=FieldConfig(
                    name="reference",
                    type="object",
                    properties={
                        "name": FieldConfig(
                            name="name",
                            label="Name",
                            type="text",
                            required=True
                        ),
                        "relationship": FieldConfig(
                            name="relationship",
                            label="Relationship",
                            type="enum",
                            required=True,
                            enum_definition_id=5  # relationship_type
                        ),
                        "phone": FieldConfig(
                            name="phone",
                            label="Phone Number",
                            type="ph_mobile_number",
                            required=True
                        )
                    }
                )
            )
        ]
    )
    
    result = await schema_generator.generate_schema(form_builder)
    
    print("\nComplex Fields:")
    print("  - Address (nested object)")
    print("  - References (array of objects)")
    print("\nValidation Rules:")
    print("  - TIN format: XXX-XXX-XXX-XXX")
    print("  - SSS format: XX-XXXXXXX-X")
    print("  - Minimum annual income: PHP 120,000")


async def example_form_with_conditionals(db: AsyncSession):
    """Example: Form with conditional logic"""
    print("\n🔀 Example 4: Form with Conditional Logic")
    print("=" * 60)
    
    schema_generator = FormSchemaGeneratorService(db)
    
    form_builder = FormSchemaBuilder(
        title="Employment Verification Form",
        description="Form with conditional required fields",
        fields=[
            FieldConfig(
                name="employment_status",
                label="Employment Status",
                type="enum",
                required=True,
                options=[
                    {"value": "employed", "label": "Employed"},
                    {"value": "self_employed", "label": "Self-Employed"},
                    {"value": "unemployed", "label": "Unemployed"}
                ]
            ),
            FieldConfig(
                name="employer_name",
                label="Employer Name",
                type="text",
                required=False,
                required_when={"employment_status": "employed"},
                visible_when={"employment_status": "employed"}
            ),
            FieldConfig(
                name="employer_address",
                label="Employer Address",
                type="address",
                required=False,
                required_when={"employment_status": "employed"},
                visible_when={"employment_status": "employed"}
            ),
            FieldConfig(
                name="business_name",
                label="Business Name",
                type="text",
                required=False,
                required_when={"employment_status": "self_employed"},
                visible_when={"employment_status": "self_employed"}
            ),
            FieldConfig(
                name="business_registration",
                label="Business Registration Number",
                type="text",
                required=False,
                required_when={"employment_status": "self_employed"},
                visible_when={"employment_status": "self_employed"}
            )
        ]
    )
    
    result = await schema_generator.generate_schema(form_builder)
    
    print("\nConditional Logic:")
    print("  - If employed: employer_name and employer_address required")
    print("  - If self-employed: business_name and business_registration required")
    print("  - If unemployed: no additional fields required")


async def main():
    """Run all examples"""
    print("🚀 Field Types System - Example Usage")
    print("=" * 60)
    
    async with AsyncSessionLocal() as db:
        try:
            await example_simple_contact_form(db)
            await example_loan_application(db)
            await example_credit_card_application(db)
            await example_form_with_conditionals(db)
            
            print("\n" + "=" * 60)
            print("✨ All examples completed successfully!")
            print("\nNext Steps:")
            print("  1. Run the seed script: python scripts/seed_field_types.py")
            print("  2. Create form templates using these schemas")
            print("  3. Test validation with form submissions")
            print("  4. Explore the API endpoints in Swagger UI")
            
        except Exception as e:
            print(f"\n❌ Error running examples: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
