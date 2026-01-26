"""
Seed sample form templates for each bank
Demonstrates all field types, enums, validation, and conditional logic
"""
import asyncio
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import AsyncSessionLocal
from app.repositories.forms import BankRepository, FormTemplateRepository
from app.services.field_types import FormSchemaGeneratorService
from app.schemas.field_types import FormSchemaBuilder, FieldConfig


async def get_or_create_bank(db: AsyncSession, name: str, code: str):
    """Get existing bank or create new one"""
    bank_repo = BankRepository()
    
    # Try to get existing bank
    result = await bank_repo.get_by_code(db, code)
    if result:
        return result
    
    # Create new bank
    return await bank_repo.create(
        db=db,
        name=name,
        code=code,
        description=f"{name} - Demo Bank",
        active=True
    )


async def create_template_for_bank(
    db: AsyncSession,
    bank_id: int,
    name: str,
    version: str,
    form_builder: FormSchemaBuilder
):
    """Create form template using schema generator"""
    schema_generator = FormSchemaGeneratorService(db)
    template_repo = FormTemplateRepository()
    
    # Generate schema
    schema_result = await schema_generator.generate_schema(form_builder)
    
    # Check if template already exists
    existing = await template_repo.get_by_bank_and_type(db, bank_id, name, version)
    if existing:
        print(f"  ⏭️  Template '{name}' v{version} already exists")
        return existing
    
    # Create template
    template = await template_repo.create(
        db=db,
        bank_id=bank_id,
        name=name,
        version=version,
        form_type=name.lower().replace(" ", "_"),
        schema_json=schema_result["schema_json"],
        fields=schema_result["fields"],
        ui_schema=schema_result["ui_schema"],
        description=form_builder.description,
        active=True,
        created_by="system"
    )
    
    print(f"  ✅ Created template: {name} v{version}")
    return template


async def seed_bdo_templates(db: AsyncSession):
    """Seed BDO templates"""
    print("\n🏦 BDO (Banco de Oro) Templates")
    print("=" * 60)
    
    bank = await get_or_create_bank(db, "Banco de Oro", "BDO")
    
    # 1. Credit Card Application
    credit_card_form = FormSchemaBuilder(
        title="BDO Credit Card Application",
        description="Apply for a BDO credit card",
        fields=[
            # Personal Information
            FieldConfig(
                name="full_name",
                label="Full Name",
                type="full_name",
                required=True,
                placeholder="Juan Dela Cruz"
            ),
            FieldConfig(
                name="email",
                label="Email Address",
                type="email",
                required=True,
                placeholder="juan.delacruz@email.com"
            ),
            FieldConfig(
                name="mobile_number",
                label="Mobile Number",
                type="ph_mobile_number",
                required=True,
                placeholder="+639171234567"
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
                options=[
                    {"value": "male", "label": "Male"},
                    {"value": "female", "label": "Female"}
                ]
            ),
            FieldConfig(
                name="marital_status",
                label="Marital Status",
                type="enum",
                required=True,
                options=[
                    {"value": "single", "label": "Single"},
                    {"value": "married", "label": "Married"},
                    {"value": "divorced", "label": "Divorced"},
                    {"value": "widowed", "label": "Widowed"}
                ]
            ),
            
            # Employment Information
            FieldConfig(
                name="employment_status",
                label="Employment Status",
                type="enum",
                required=True,
                options=[
                    {"value": "employed", "label": "Employed"},
                    {"value": "self_employed", "label": "Self-Employed"},
                    {"value": "retired", "label": "Retired"}
                ]
            ),
            FieldConfig(
                name="monthly_income",
                label="Monthly Income (PHP)",
                type="monthly_salary",
                required=True,
                validation={"minimum": 15000}
            ),
            
            # Government IDs
            FieldConfig(
                name="tin",
                label="Tax Identification Number",
                type="ph_tin",
                required=True
            ),
            FieldConfig(
                name="sss_number",
                label="SSS Number (Optional)",
                type="ph_sss_number",
                required=False
            ),
            
            # Address
            FieldConfig(
                name="home_address",
                label="Home Address",
                type="address",
                required=True
            ),
            
            # Credit Card Preferences
            FieldConfig(
                name="card_type",
                label="Preferred Card Type",
                type="enum",
                required=True,
                options=[
                    {"value": "classic", "label": "BDO Classic Mastercard"},
                    {"value": "gold", "label": "BDO Gold Mastercard"},
                    {"value": "platinum", "label": "BDO Platinum Mastercard"},
                    {"value": "amex", "label": "BDO American Express"}
                ]
            ),
            FieldConfig(
                name="has_existing_credit_card",
                label="Do you have an existing credit card?",
                type="boolean",
                required=True,
                default=False
            )
        ]
    )
    
    await create_template_for_bank(db, bank.id, "Credit Card Application", "1.0.0", credit_card_form)
    
    # 2. Personal Loan Application
    personal_loan_form = FormSchemaBuilder(
        title="BDO Personal Loan",
        description="Apply for a personal loan from BDO",
        fields=[
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
                name="mobile",
                label="Mobile Number",
                type="ph_mobile_number",
                required=True
            ),
            FieldConfig(
                name="monthly_income",
                label="Monthly Income",
                type="monthly_salary",
                required=True,
                validation={"minimum": 20000}
            ),
            FieldConfig(
                name="loan_amount",
                label="Loan Amount (PHP)",
                type="currency",
                required=True,
                validation={"minimum": 20000, "maximum": 2000000}
            ),
            FieldConfig(
                name="loan_term",
                label="Loan Term (Months)",
                type="integer",
                required=True,
                validation={"minimum": 6, "maximum": 60}
            ),
            FieldConfig(
                name="loan_purpose",
                label="Purpose of Loan",
                type="enum",
                required=True,
                options=[
                    {"value": "business", "label": "Business Capital"},
                    {"value": "education", "label": "Education"},
                    {"value": "medical", "label": "Medical Emergency"},
                    {"value": "home_improvement", "label": "Home Improvement"},
                    {"value": "debt_consolidation", "label": "Debt Consolidation"}
                ]
            ),
            FieldConfig(
                name="employment_type",
                label="Employment Type",
                type="enum",
                required=True,
                options=[
                    {"value": "regular", "label": "Regular Employee"},
                    {"value": "contractual", "label": "Contractual"},
                    {"value": "self_employed", "label": "Self-Employed"}
                ]
            )
        ]
    )
    
    await create_template_for_bank(db, bank.id, "Personal Loan Application", "1.0.0", personal_loan_form)


async def seed_bpi_templates(db: AsyncSession):
    """Seed BPI templates"""
    print("\n🏦 BPI (Bank of the Philippine Islands) Templates")
    print("=" * 60)
    
    bank = await get_or_create_bank(db, "Bank of the Philippine Islands", "BPI")
    
    # Savings Account Opening
    savings_account_form = FormSchemaBuilder(
        title="BPI Savings Account Application",
        description="Open a BPI savings account",
        fields=[
            # Personal Details
            FieldConfig(
                name="first_name",
                label="First Name",
                type="text",
                required=True,
                validation={"minLength": 2, "maxLength": 50}
            ),
            FieldConfig(
                name="middle_name",
                label="Middle Name",
                type="text",
                required=False,
                validation={"maxLength": 50}
            ),
            FieldConfig(
                name="last_name",
                label="Last Name",
                type="text",
                required=True,
                validation={"minLength": 2, "maxLength": 50}
            ),
            FieldConfig(
                name="suffix",
                label="Suffix",
                type="enum",
                required=False,
                options=[
                    {"value": "jr", "label": "Jr."},
                    {"value": "sr", "label": "Sr."},
                    {"value": "ii", "label": "II"},
                    {"value": "iii", "label": "III"}
                ]
            ),
            FieldConfig(
                name="birth_date",
                label="Date of Birth",
                type="date",
                required=True
            ),
            FieldConfig(
                name="nationality",
                label="Nationality",
                type="text",
                required=True,
                default="Filipino"
            ),
            FieldConfig(
                name="civil_status",
                label="Civil Status",
                type="enum",
                required=True,
                options=[
                    {"value": "single", "label": "Single"},
                    {"value": "married", "label": "Married"},
                    {"value": "widowed", "label": "Widowed"},
                    {"value": "separated", "label": "Separated"}
                ]
            ),
            
            # Contact Information
            FieldConfig(
                name="email_address",
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
                name="home_phone",
                label="Home Phone (Optional)",
                type="phone",
                required=False
            ),
            
            # Address
            FieldConfig(
                name="current_address",
                label="Current Address",
                type="address",
                required=True
            ),
            FieldConfig(
                name="years_at_current_address",
                label="Years at Current Address",
                type="integer",
                required=True,
                validation={"minimum": 0, "maximum": 100}
            ),
            
            # Employment
            FieldConfig(
                name="occupation",
                label="Occupation",
                type="text",
                required=True,
                validation={"minLength": 2, "maxLength": 100}
            ),
            FieldConfig(
                name="employer_name",
                label="Employer Name",
                type="text",
                required=True
            ),
            FieldConfig(
                name="monthly_income_range",
                label="Monthly Income Range",
                type="enum",
                required=True,
                options=[
                    {"value": "below_20k", "label": "Below ₱20,000"},
                    {"value": "20k_40k", "label": "₱20,000 - ₱40,000"},
                    {"value": "40k_60k", "label": "₱40,000 - ₱60,000"},
                    {"value": "60k_100k", "label": "₱60,000 - ₱100,000"},
                    {"value": "above_100k", "label": "Above ₱100,000"}
                ]
            ),
            
            # Account Details
            FieldConfig(
                name="account_type",
                label="Account Type",
                type="enum",
                required=True,
                options=[
                    {"value": "regular", "label": "Regular Savings"},
                    {"value": "pamana", "label": "BPI Pamana Padala"},
                    {"value": "young_savers", "label": "BPI Young Savers"}
                ]
            ),
            FieldConfig(
                name="initial_deposit",
                label="Initial Deposit Amount (PHP)",
                type="currency",
                required=True,
                validation={"minimum": 3000},
                description="Minimum initial deposit: ₱3,000"
            )
        ]
    )
    
    await create_template_for_bank(db, bank.id, "Savings Account Application", "1.0.0", savings_account_form)
    
    # Auto Loan
    auto_loan_form = FormSchemaBuilder(
        title="BPI Auto Loan Application",
        description="Finance your dream car with BPI",
        fields=[
            FieldConfig(
                name="applicant_name",
                label="Full Name",
                type="full_name",
                required=True
            ),
            FieldConfig(
                name="contact_number",
                label="Contact Number",
                type="ph_mobile_number",
                required=True
            ),
            FieldConfig(
                name="email",
                label="Email Address",
                type="email",
                required=True
            ),
            
            # Vehicle Information
            FieldConfig(
                name="vehicle_type",
                label="Vehicle Type",
                type="enum",
                required=True,
                options=[
                    {"value": "brand_new", "label": "Brand New"},
                    {"value": "second_hand", "label": "Second Hand"}
                ]
            ),
            FieldConfig(
                name="vehicle_make",
                label="Vehicle Make",
                type="text",
                required=True,
                placeholder="e.g., Toyota, Honda, Mitsubishi"
            ),
            FieldConfig(
                name="vehicle_model",
                label="Vehicle Model",
                type="text",
                required=True,
                placeholder="e.g., Vios, Civic, Montero"
            ),
            FieldConfig(
                name="vehicle_year",
                label="Vehicle Year",
                type="integer",
                required=True,
                validation={"minimum": 2015, "maximum": 2027}
            ),
            FieldConfig(
                name="vehicle_price",
                label="Vehicle Price (PHP)",
                type="currency",
                required=True,
                validation={"minimum": 300000, "maximum": 10000000}
            ),
            
            # Loan Details
            FieldConfig(
                name="down_payment",
                label="Down Payment (PHP)",
                type="currency",
                required=True,
                validation={"minimum": 0}
            ),
            FieldConfig(
                name="loan_term_years",
                label="Loan Term (Years)",
                type="integer",
                required=True,
                validation={"minimum": 1, "maximum": 5}
            ),
            
            # Financial Information
            FieldConfig(
                name="gross_monthly_income",
                label="Gross Monthly Income",
                type="monthly_salary",
                required=True,
                validation={"minimum": 25000}
            ),
            FieldConfig(
                name="employment_status",
                label="Employment Status",
                type="enum",
                required=True,
                options=[
                    {"value": "employed", "label": "Employed"},
                    {"value": "self_employed", "label": "Self-Employed"},
                    {"value": "business_owner", "label": "Business Owner"}
                ]
            )
        ]
    )
    
    await create_template_for_bank(db, bank.id, "Auto Loan Application", "1.0.0", auto_loan_form)


async def seed_metrobank_templates(db: AsyncSession):
    """Seed Metrobank templates"""
    print("\n🏦 Metrobank Templates")
    print("=" * 60)
    
    bank = await get_or_create_bank(db, "Metropolitan Bank & Trust Company", "METROBANK")
    
    # Home Loan Application
    home_loan_form = FormSchemaBuilder(
        title="Metrobank Home Loan",
        description="Housing loan application for Metrobank",
        fields=[
            # Borrower Information
            FieldConfig(
                name="borrower_name",
                label="Borrower's Full Name",
                type="full_name",
                required=True
            ),
            FieldConfig(
                name="spouse_name",
                label="Spouse Name (if married)",
                type="full_name",
                required=False
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
                name="date_of_birth",
                label="Date of Birth",
                type="date",
                required=True
            ),
            FieldConfig(
                name="marital_status",
                label="Marital Status",
                type="enum",
                required=True,
                options=[
                    {"value": "single", "label": "Single"},
                    {"value": "married", "label": "Married"},
                    {"value": "widowed", "label": "Widowed"}
                ]
            ),
            
            # Property Information
            FieldConfig(
                name="property_type",
                label="Property Type",
                type="enum",
                required=True,
                options=[
                    {"value": "house_and_lot", "label": "House and Lot"},
                    {"value": "condominium", "label": "Condominium"},
                    {"value": "townhouse", "label": "Townhouse"},
                    {"value": "lot_only", "label": "Lot Only"}
                ]
            ),
            FieldConfig(
                name="property_location",
                label="Property Location",
                type="address",
                required=True
            ),
            FieldConfig(
                name="property_value",
                label="Property Value (PHP)",
                type="currency",
                required=True,
                validation={"minimum": 500000, "maximum": 50000000}
            ),
            FieldConfig(
                name="loan_amount_requested",
                label="Loan Amount Requested (PHP)",
                type="currency",
                required=True,
                validation={"minimum": 300000}
            ),
            FieldConfig(
                name="loan_term_years",
                label="Loan Term (Years)",
                type="integer",
                required=True,
                validation={"minimum": 5, "maximum": 30}
            ),
            
            # Employment and Income
            FieldConfig(
                name="employment_type",
                label="Employment Type",
                type="enum",
                required=True,
                options=[
                    {"value": "local_employed", "label": "Locally Employed"},
                    {"value": "ofw", "label": "OFW"},
                    {"value": "self_employed", "label": "Self-Employed"},
                    {"value": "professional", "label": "Professional"}
                ]
            ),
            FieldConfig(
                name="employer_name",
                label="Employer/Business Name",
                type="text",
                required=True
            ),
            FieldConfig(
                name="gross_monthly_income",
                label="Gross Monthly Income",
                type="monthly_salary",
                required=True,
                validation={"minimum": 30000}
            ),
            FieldConfig(
                name="years_employed",
                label="Years with Current Employer",
                type="integer",
                required=True,
                validation={"minimum": 0, "maximum": 50}
            ),
            
            # Co-borrower (if applicable)
            FieldConfig(
                name="has_co_borrower",
                label="Do you have a co-borrower?",
                type="boolean",
                required=True,
                default=False
            )
        ]
    )
    
    await create_template_for_bank(db, bank.id, "Home Loan Application", "1.0.0", home_loan_form)
    
    # Business Loan
    business_loan_form = FormSchemaBuilder(
        title="Metrobank Business Loan",
        description="Small and Medium Enterprise (SME) loan application",
        fields=[
            # Business Owner Information
            FieldConfig(
                name="owner_name",
                label="Business Owner Name",
                type="full_name",
                required=True
            ),
            FieldConfig(
                name="contact_number",
                label="Contact Number",
                type="ph_mobile_number",
                required=True
            ),
            FieldConfig(
                name="email_address",
                label="Email Address",
                type="email",
                required=True
            ),
            
            # Business Information
            FieldConfig(
                name="business_name",
                label="Business Name",
                type="text",
                required=True,
                validation={"minLength": 2, "maxLength": 200}
            ),
            FieldConfig(
                name="business_type",
                label="Type of Business",
                type="enum",
                required=True,
                options=[
                    {"value": "retail", "label": "Retail"},
                    {"value": "manufacturing", "label": "Manufacturing"},
                    {"value": "services", "label": "Services"},
                    {"value": "trading", "label": "Trading"},
                    {"value": "food", "label": "Food & Beverage"},
                    {"value": "other", "label": "Other"}
                ]
            ),
            FieldConfig(
                name="years_in_business",
                label="Years in Business",
                type="integer",
                required=True,
                validation={"minimum": 1, "maximum": 100}
            ),
            FieldConfig(
                name="business_address",
                label="Business Address",
                type="address",
                required=True
            ),
            FieldConfig(
                name="business_tin",
                label="Business TIN",
                type="ph_tin",
                required=True
            ),
            
            # Financial Information
            FieldConfig(
                name="annual_revenue",
                label="Annual Revenue (PHP)",
                type="currency",
                required=True,
                validation={"minimum": 500000}
            ),
            FieldConfig(
                name="monthly_expenses",
                label="Monthly Operating Expenses (PHP)",
                type="currency",
                required=True,
                validation={"minimum": 0}
            ),
            
            # Loan Details
            FieldConfig(
                name="loan_amount",
                label="Loan Amount (PHP)",
                type="currency",
                required=True,
                validation={"minimum": 100000, "maximum": 10000000}
            ),
            FieldConfig(
                name="loan_purpose",
                label="Purpose of Loan",
                type="enum",
                required=True,
                options=[
                    {"value": "working_capital", "label": "Working Capital"},
                    {"value": "equipment", "label": "Equipment Purchase"},
                    {"value": "expansion", "label": "Business Expansion"},
                    {"value": "inventory", "label": "Inventory"},
                    {"value": "renovation", "label": "Renovation"}
                ]
            ),
            FieldConfig(
                name="repayment_term_months",
                label="Preferred Repayment Term (Months)",
                type="integer",
                required=True,
                validation={"minimum": 12, "maximum": 60}
            ),
            
            # Collateral
            FieldConfig(
                name="has_collateral",
                label="Can you provide collateral?",
                type="boolean",
                required=True
            ),
            FieldConfig(
                name="number_of_employees",
                label="Number of Employees",
                type="integer",
                required=True,
                validation={"minimum": 1, "maximum": 1000}
            )
        ]
    )
    
    await create_template_for_bank(db, bank.id, "Business Loan Application", "1.0.0", business_loan_form)


async def seed_security_bank_templates(db: AsyncSession):
    """Seed Security Bank templates"""
    print("\n🏦 Security Bank Templates")
    print("=" * 60)
    
    bank = await get_or_create_bank(db, "Security Bank Corporation", "SECURITYBANK")
    
    # Time Deposit Account
    time_deposit_form = FormSchemaBuilder(
        title="Security Bank Time Deposit",
        description="Open a time deposit account",
        fields=[
            FieldConfig(
                name="account_holder_name",
                label="Account Holder Name",
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
                name="birth_date",
                label="Date of Birth",
                type="date",
                required=True
            ),
            FieldConfig(
                name="tin",
                label="Tax Identification Number",
                type="ph_tin",
                required=True
            ),
            
            # Deposit Details
            FieldConfig(
                name="deposit_amount",
                label="Deposit Amount (PHP)",
                type="currency",
                required=True,
                validation={"minimum": 50000},
                description="Minimum deposit: ₱50,000"
            ),
            FieldConfig(
                name="deposit_term",
                label="Deposit Term",
                type="enum",
                required=True,
                options=[
                    {"value": "30_days", "label": "30 Days"},
                    {"value": "60_days", "label": "60 Days"},
                    {"value": "90_days", "label": "90 Days"},
                    {"value": "180_days", "label": "180 Days"},
                    {"value": "1_year", "label": "1 Year"},
                    {"value": "2_years", "label": "2 Years"},
                    {"value": "5_years", "label": "5 Years"}
                ]
            ),
            FieldConfig(
                name="auto_renewal",
                label="Auto-Renewal",
                type="enum",
                required=True,
                options=[
                    {"value": "principal_and_interest", "label": "Principal and Interest"},
                    {"value": "principal_only", "label": "Principal Only"},
                    {"value": "no_renewal", "label": "No Auto-Renewal"}
                ]
            ),
            FieldConfig(
                name="contact_address",
                label="Contact Address",
                type="address",
                required=True
            ),
            FieldConfig(
                name="source_of_funds",
                label="Source of Funds",
                type="enum",
                required=True,
                options=[
                    {"value": "salary", "label": "Salary/Income"},
                    {"value": "business", "label": "Business Income"},
                    {"value": "savings", "label": "Savings"},
                    {"value": "inheritance", "label": "Inheritance"},
                    {"value": "investment", "label": "Investment Returns"}
                ]
            )
        ]
    )
    
    await create_template_for_bank(db, bank.id, "Time Deposit Application", "1.0.0", time_deposit_form)


async def seed_rcbc_templates(db: AsyncSession):
    """Seed RCBC templates"""
    print("\n🏦 RCBC (Rizal Commercial Banking Corporation) Templates")
    print("=" * 60)
    
    bank = await get_or_create_bank(db, "Rizal Commercial Banking Corporation", "RCBC")
    
    # OFW (Overseas Filipino Worker) Loan
    ofw_loan_form = FormSchemaBuilder(
        title="RCBC OFW Loan",
        description="Special loan program for Overseas Filipino Workers",
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
                name="mobile_philippines",
                label="Philippine Mobile Number",
                type="ph_mobile_number",
                required=True
            ),
            FieldConfig(
                name="mobile_abroad",
                label="Mobile Number Abroad",
                type="phone",
                required=True
            ),
            FieldConfig(
                name="date_of_birth",
                label="Date of Birth",
                type="date",
                required=True
            ),
            FieldConfig(
                name="gender",
                label="Gender",
                type="enum",
                required=True,
                options=[
                    {"value": "male", "label": "Male"},
                    {"value": "female", "label": "Female"}
                ]
            ),
            
            # OFW Details
            FieldConfig(
                name="country_of_employment",
                label="Country of Employment",
                type="text",
                required=True
            ),
            FieldConfig(
                name="occupation_abroad",
                label="Occupation/Position Abroad",
                type="text",
                required=True
            ),
            FieldConfig(
                name="employer_name_abroad",
                label="Employer Name",
                type="text",
                required=True
            ),
            FieldConfig(
                name="years_abroad",
                label="Years Working Abroad",
                type="integer",
                required=True,
                validation={"minimum": 1, "maximum": 50}
            ),
            FieldConfig(
                name="monthly_salary_abroad",
                label="Monthly Salary (in PHP equivalent)",
                type="monthly_salary",
                required=True,
                validation={"minimum": 30000}
            ),
            FieldConfig(
                name="contract_end_date",
                label="Contract End Date",
                type="date",
                required=True
            ),
            
            # Philippine Address
            FieldConfig(
                name="philippine_address",
                label="Philippine Address",
                type="address",
                required=True
            ),
            
            # Loan Details
            FieldConfig(
                name="loan_amount",
                label="Loan Amount (PHP)",
                type="currency",
                required=True,
                validation={"minimum": 50000, "maximum": 1000000}
            ),
            FieldConfig(
                name="loan_purpose",
                label="Purpose of Loan",
                type="enum",
                required=True,
                options=[
                    {"value": "home_construction", "label": "Home Construction/Renovation"},
                    {"value": "business_capital", "label": "Business Capital"},
                    {"value": "education", "label": "Children's Education"},
                    {"value": "medical", "label": "Medical Expenses"},
                    {"value": "emergency", "label": "Emergency Needs"}
                ]
            ),
            FieldConfig(
                name="loan_term_months",
                label="Loan Term (Months)",
                type="integer",
                required=True,
                validation={"minimum": 12, "maximum": 36}
            ),
            
            # Beneficiary Information
            FieldConfig(
                name="beneficiary_name",
                label="Beneficiary Name (Family in PH)",
                type="full_name",
                required=True
            ),
            FieldConfig(
                name="beneficiary_relationship",
                label="Relationship to Beneficiary",
                type="enum",
                required=True,
                options=[
                    {"value": "spouse", "label": "Spouse"},
                    {"value": "parent", "label": "Parent"},
                    {"value": "child", "label": "Child"},
                    {"value": "sibling", "label": "Sibling"}
                ]
            ),
            FieldConfig(
                name="beneficiary_mobile",
                label="Beneficiary Mobile Number",
                type="ph_mobile_number",
                required=True
            )
        ]
    )
    
    await create_template_for_bank(db, bank.id, "OFW Loan Application", "1.0.0", ofw_loan_form)


async def main():
    """Main seeding function"""
    print("🌱 Seeding Sample Form Templates for All Banks")
    print("=" * 60)
    print("This will create diverse form templates demonstrating:")
    print("  ✓ All predefined field types")
    print("  ✓ Custom field types (PH mobile, TIN, SSS)")
    print("  ✓ Enum fields with various options")
    print("  ✓ Validation rules (min/max, patterns)")
    print("  ✓ Complex types (address, nested objects)")
    print("  ✓ Different form purposes (loans, accounts, cards)")
    print()
    
    async with AsyncSessionLocal() as db:
        try:
            total_templates = 0
            
            # Seed templates for each bank
            await seed_bdo_templates(db)
            total_templates += 2
            
            await seed_bpi_templates(db)
            total_templates += 2
            
            await seed_metrobank_templates(db)
            total_templates += 2
            
            await seed_security_bank_templates(db)
            total_templates += 1
            
            await seed_rcbc_templates(db)
            total_templates += 1
            
            print("\n" + "=" * 60)
            print("✨ Sample Templates Created Successfully!")
            print(f"   Total templates: {total_templates}")
            print()
            print("📊 Summary by Bank:")
            print("   • BDO: Credit Card, Personal Loan")
            print("   • BPI: Savings Account, Auto Loan")
            print("   • Metrobank: Home Loan, Business Loan")
            print("   • Security Bank: Time Deposit")
            print("   • RCBC: OFW Loan")
            print()
            print("🎯 Next Steps:")
            print("   1. View templates in Swagger UI: /api/v1/docs")
            print("   2. Test GET /api/v1/templates")
            print("   3. Create submissions using these templates")
            print("   4. Test validation with form data")
            
        except Exception as e:
            print(f"\n❌ Error during seeding: {e}")
            import traceback
            traceback.print_exc()
            raise


if __name__ == "__main__":
    asyncio.run(main())
