import asyncio
import sys
from pathlib import Path

# Add project root to path
backend_path = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_path))

from app.db.session import AsyncSessionLocal
from app.models.forms import FormTemplate
from app.services.form_validation import FormValidationService
from sqlalchemy import select

async def verify_validation():
    async with AsyncSessionLocal() as session:
        # Get BDO template
        result = await session.execute(select(FormTemplate).where(FormTemplate.name == "BDO Loan Application Form"))
        template_obj = result.scalar_one_or_none()
        
        if not template_obj:
            print("❌ BDO Template not found")
            return

        template_data = {
            "schema_json": template_obj.schema_json,
            "fields": template_obj.fields
        }

        # Test Case 1: Valid Employed
        data1 = {
            "applicant_name": "John Doe",
            "email": "john@example.com",
            "phone": "09123456789",
            "civil_status": "Single",
            "employment_status": "Employed",
            "employer_name": "Acme Corp",
            "monthly_income": 50000,
            "loan_amount": 100000,
            "loan_purpose": "Education",
            "valid_id": "file_token_123",
            "proof_of_income": "file_token_456"
        }
        res1 = FormValidationService.validate_submission(data1, template_data)
        print(f"Test 1 (Valid Employed): {'✅ PASS' if res1.is_valid else '❌ FAIL'}")
        if not res1.is_valid:
            print(f"Errors: {res1.errors}")

        # Test Case 2: Missing employer_name when Employed
        data2 = {
            "applicant_name": "John Doe",
            "email": "john@example.com",
            "phone": "09123456789",
            "civil_status": "Single",
            "employment_status": "Employed",
            "monthly_income": 50000,
            "loan_amount": 100000,
            "loan_purpose": "Education",
            "valid_id": "file_token_123",
            "proof_of_income": "file_token_456"
        }
        res2 = FormValidationService.validate_submission(data2, template_data)
        print(f"Test 2 (Missing employer_name): {'✅ PASS' if not res2.is_valid else '❌ FAIL'}")
        if not res2.is_valid:
             print(f"Expected Error found: {any(e.field == 'employer_name' for e in res2.errors)}")

        # Test Case 3: Missing spouse_name when Married
        data3 = {
            "applicant_name": "Married Doe",
            "email": "married@example.com",
            "phone": "09112223344",
            "civil_status": "Married",
            # spouse_name missing
            "employment_status": "Self-Employed",
            "monthly_income": 200000,
            "loan_amount": 1000000,
            "loan_purpose": "Home Renovation",
            "valid_id": "file_token_123",
            "proof_of_income": "file_token_456"
        }
        res3 = FormValidationService.validate_submission(data3, template_data)
        print(f"Test 3 (Missing Spouse Name): {'✅ PASS' if not res3.is_valid else '❌ FAIL'}")
        if not res3.is_valid:
             print(f"Expected Error ('spouse_name'): {any(e.field == 'spouse_name' for e in res3.errors)}")

if __name__ == "__main__":
    asyncio.run(verify_validation())
