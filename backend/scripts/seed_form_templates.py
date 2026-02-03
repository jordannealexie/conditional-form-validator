"""
Seed Form Templates with JSON Schema Draft-07 Compliance
Demonstrates: nested conditionals, various field types, complex validation, database options
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import AsyncSessionLocal as async_session_maker
from app.models.forms import Bank, FormTemplate
from sqlalchemy import select


# ============================================================================
# STAGE 1: Simple Form - Credit Card Application (BPI)
# Demonstrates: Basic types, simple conditionals, default values
# ============================================================================
BPI_CREDIT_CARD_TEMPLATE = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Credit Card Application",
    "description": "BPI Credit Card Application Form",
    "type": "object",
    "required": ["applicant_type", "full_name", "email", "phone", "monthly_income"],
    "properties": {
        "applicant_type": {
            "type": "string",
            "title": "Applicant Type",
            "enum": ["individual", "corporate"],
            "default": "individual",
            "description": "Type of credit card applicant"
        },
        "full_name": {
            "type": "string",
            "title": "Full Name",
            "minLength": 2,
            "maxLength": 100,
            "pattern": "^[a-zA-Z\\s.'-]+$",
            "description": "Legal full name as shown on valid ID"
        },
        "email": {
            "type": "string",
            "title": "Email Address",
            "format": "email",
            "description": "Valid email address for correspondence"
        },
        "phone": {
            "type": "string",
            "title": "Phone Number",
            "pattern": "^(\\+63|0)[0-9]{10}$",
            "description": "Philippine mobile number (e.g., +639171234567 or 09171234567)"
        },
        "monthly_income": {
            "type": "number",
            "title": "Monthly Income (PHP)",
            "minimum": 0,
            "maximum": 100000000,
            "multipleOf": 0.01,
            "description": "Gross monthly income in Philippine Peso"
        },
        "card_type": {
            "type": "string",
            "title": "Preferred Card Type",
            "enum": ["classic", "gold", "platinum", "signature"],
            "default": "classic"
        },
        "employment_status": {
            "type": "string",
            "title": "Employment Status",
            "enum": ["employed", "self_employed", "unemployed", "retired"],
            "default": "employed"
        }
    },
    "if": {
        "properties": {
            "applicant_type": {"const": "corporate"}
        }
    },
    "then": {
        "required": ["company_name", "company_tin"],
        "properties": {
            "company_name": {
                "type": "string",
                "title": "Company Name",
                "minLength": 2,
                "maxLength": 200
            },
            "company_tin": {
                "type": "string",
                "title": "Company TIN",
                "pattern": "^[0-9]{9,12}$"
            }
        }
    },
    "else": {
        "required": ["date_of_birth"],
        "properties": {
            "date_of_birth": {
                "type": "string",
                "title": "Date of Birth",
                "format": "date",
                "description": "Birth date in YYYY-MM-DD format"
            }
        }
    }
}


# ============================================================================
# STAGE 2: Complex Form - Housing Loan Application (BDO)
# Demonstrates: Nested conditionals, complex types, allOf/anyOf/oneOf, address type
# ============================================================================
BDO_HOUSING_LOAN_TEMPLATE = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Housing Loan Application",
    "description": "BDO Unibank Housing Loan Application with nested conditionals",
    "type": "object",
    "required": ["loan_type", "applicant_info", "property_info", "loan_amount"],
    "properties": {
        "loan_type": {
            "type": "string",
            "title": "Loan Type",
            "enum": ["new_purchase", "refinancing", "home_equity", "construction"],
            "default": "new_purchase"
        },
        "loan_amount": {
            "type": "number",
            "title": "Loan Amount (PHP)",
            "minimum": 500000,
            "maximum": 50000000,
            "multipleOf": 1000,
            "description": "Loan amount in Philippine Peso"
        },
        "loan_term_years": {
            "type": "integer",
            "title": "Loan Term (Years)",
            "minimum": 5,
            "maximum": 30,
            "default": 20
        },
        "interest_rate_type": {
            "type": "string",
            "title": "Interest Rate Type",
            "enum": ["fixed", "variable"],
            "default": "fixed"
        },
        "applicant_info": {
            "type": "object",
            "title": "Applicant Information",
            "required": ["first_name", "last_name", "email", "phone", "citizenship"],
            "properties": {
                "first_name": {
                    "type": "string",
                    "title": "First Name",
                    "minLength": 1,
                    "maxLength": 50
                },
                "middle_name": {
                    "type": "string",
                    "title": "Middle Name",
                    "maxLength": 50
                },
                "last_name": {
                    "type": "string",
                    "title": "Last Name",
                    "minLength": 1,
                    "maxLength": 50
                },
                "email": {
                    "type": "string",
                    "title": "Email",
                    "format": "email"
                },
                "phone": {
                    "type": "string",
                    "title": "Phone",
                    "pattern": "^(\\+63|0)[0-9]{10}$"
                },
                "date_of_birth": {
                    "type": "string",
                    "title": "Date of Birth",
                    "format": "date"
                },
                "citizenship": {
                    "type": "string",
                    "title": "Citizenship",
                    "enum": ["filipino", "foreign_resident", "foreign_non_resident"],
                    "default": "filipino"
                },
                "civil_status": {
                    "type": "string",
                    "title": "Civil Status",
                    "enum": ["single", "married", "widowed", "separated", "divorced"],
                    "default": "single"
                }
            }
        },
        "property_info": {
            "type": "object",
            "title": "Property Information",
            "required": ["property_type", "property_address", "property_value"],
            "properties": {
                "property_type": {
                    "type": "string",
                    "title": "Property Type",
                    "enum": ["house_and_lot", "condominium", "townhouse", "lot_only"],
                    "default": "house_and_lot"
                },
                "property_address": {
                    "type": "object",
                    "title": "Property Address",
                    "required": ["street", "barangay", "city", "province", "zip_code"],
                    "properties": {
                        "street": {
                            "type": "string",
                            "title": "Street/Subdivision",
                            "minLength": 1,
                            "maxLength": 200
                        },
                        "barangay": {
                            "type": "string",
                            "title": "Barangay",
                            "minLength": 1,
                            "maxLength": 100
                        },
                        "city": {
                            "type": "string",
                            "title": "City/Municipality",
                            "minLength": 1,
                            "maxLength": 100
                        },
                        "province": {
                            "type": "string",
                            "title": "Province",
                            "minLength": 1,
                            "maxLength": 100
                        },
                        "zip_code": {
                            "type": "string",
                            "title": "ZIP Code",
                            "pattern": "^[0-9]{4}$"
                        },
                        "country": {
                            "type": "string",
                            "title": "Country",
                            "default": "Philippines"
                        }
                    }
                },
                "property_value": {
                    "type": "number",
                    "title": "Property Value (PHP)",
                    "minimum": 500000,
                    "maximum": 100000000,
                    "multipleOf": 1000
                }
            }
        },
        "employment_info": {
            "type": "object",
            "title": "Employment Information",
            "required": ["employment_type", "monthly_income"],
            "properties": {
                "employment_type": {
                    "type": "string",
                    "title": "Employment Type",
                    "enum": ["employed", "self_employed", "business_owner", "professional"],
                    "default": "employed"
                },
                "monthly_income": {
                    "type": "number",
                    "title": "Monthly Gross Income (PHP)",
                    "minimum": 0,
                    "maximum": 100000000,
                    "multipleOf": 0.01
                },
                "years_in_current_job": {
                    "type": "number",
                    "title": "Years in Current Job",
                    "minimum": 0,
                    "maximum": 50,
                    "multipleOf": 0.5
                }
            }
        },
        "co_borrower_required": {
            "type": "boolean",
            "title": "Add Co-Borrower",
            "default": False
        }
    },
    "allOf": [
        {
            "if": {
                "properties": {
                    "applicant_info": {
                        "properties": {
                            "citizenship": {"const": "foreign_resident"}
                        }
                    }
                }
            },
            "then": {
                "properties": {
                    "applicant_info": {
                        "required": ["work_permit_number"],
                        "properties": {
                            "work_permit_number": {
                                "type": "string",
                                "title": "Work Permit Number",
                                "minLength": 5,
                                "maxLength": 50
                            }
                        }
                    }
                }
            }
        },
        {
            "if": {
                "properties": {
                    "applicant_info": {
                        "properties": {
                            "civil_status": {"const": "married"}
                        }
                    }
                }
            },
            "then": {
                "properties": {
                    "applicant_info": {
                        "required": ["spouse_name"],
                        "properties": {
                            "spouse_name": {
                                "type": "string",
                                "title": "Spouse Full Name",
                                "minLength": 2,
                                "maxLength": 100
                            },
                            "spouse_income": {
                                "type": "number",
                                "title": "Spouse Monthly Income (PHP)",
                                "minimum": 0,
                                "maximum": 100000000,
                                "multipleOf": 0.01
                            }
                        }
                    }
                }
            }
        },
        {
            "if": {
                "properties": {
                    "loan_type": {"const": "refinancing"}
                }
            },
            "then": {
                "required": ["existing_loan_info"],
                "properties": {
                    "existing_loan_info": {
                        "type": "object",
                        "title": "Existing Loan Information",
                        "required": ["current_lender", "outstanding_balance", "monthly_amortization"],
                        "properties": {
                            "current_lender": {
                                "type": "string",
                                "title": "Current Lender",
                                "minLength": 2,
                                "maxLength": 100
                            },
                            "outstanding_balance": {
                                "type": "number",
                                "title": "Outstanding Balance (PHP)",
                                "minimum": 0,
                                "multipleOf": 0.01
                            },
                            "monthly_amortization": {
                                "type": "number",
                                "title": "Current Monthly Amortization (PHP)",
                                "minimum": 0,
                                "multipleOf": 0.01
                            }
                        }
                    }
                }
            }
        },
        {
            "if": {
                "properties": {
                    "co_borrower_required": {"const": True}
                }
            },
            "then": {
                "required": ["co_borrower_info"],
                "properties": {
                    "co_borrower_info": {
                        "type": "object",
                        "title": "Co-Borrower Information",
                        "required": ["full_name", "email", "phone", "monthly_income", "relationship"],
                        "properties": {
                            "full_name": {
                                "type": "string",
                                "title": "Full Name",
                                "minLength": 2,
                                "maxLength": 100
                            },
                            "email": {
                                "type": "string",
                                "title": "Email",
                                "format": "email"
                            },
                            "phone": {
                                "type": "string",
                                "title": "Phone",
                                "pattern": "^(\\+63|0)[0-9]{10}$"
                            },
                            "date_of_birth": {
                                "type": "string",
                                "title": "Date of Birth",
                                "format": "date"
                            },
                            "monthly_income": {
                                "type": "number",
                                "title": "Monthly Income (PHP)",
                                "minimum": 0,
                                "multipleOf": 0.01
                            },
                            "relationship": {
                                "type": "string",
                                "title": "Relationship to Applicant",
                                "enum": ["spouse", "parent", "sibling", "child", "relative", "friend"],
                                "default": "spouse"
                            }
                        }
                    }
                }
            }
        }
    ]
}


# ============================================================================
# STAGE 3: Advanced Form - Investment Account Opening (Metrobank)
# Demonstrates: anyOf, oneOf, not, rating, percentage, currency, file upload
# ============================================================================
METROBANK_INVESTMENT_TEMPLATE = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Investment Account Opening",
    "description": "Metrobank Investment Account with Risk Profiling",
    "type": "object",
    "required": ["account_type", "investor_info", "risk_profile", "initial_investment"],
    "properties": {
        "account_type": {
            "type": "string",
            "title": "Account Type",
            "enum": ["uitf", "mutual_fund", "stocks", "bonds", "time_deposit"],
            "description": "Type of investment account"
        },
        "investor_info": {
            "type": "object",
            "title": "Investor Information",
            "required": ["full_name", "email", "phone", "tin"],
            "properties": {
                "full_name": {
                    "type": "string",
                    "title": "Full Name",
                    "minLength": 2,
                    "maxLength": 100
                },
                "email": {
                    "type": "string",
                    "title": "Email",
                    "format": "email"
                },
                "phone": {
                    "type": "string",
                    "title": "Phone",
                    "pattern": "^(\\+63|0)[0-9]{10}$"
                },
                "tin": {
                    "type": "string",
                    "title": "Tax Identification Number",
                    "pattern": "^[0-9]{9,12}$"
                },
                "investor_type": {
                    "type": "string",
                    "title": "Investor Type",
                    "enum": ["individual", "corporate", "trust_account"],
                    "default": "individual"
                },
                "annual_income": {
                    "type": "number",
                    "title": "Annual Income (PHP)",
                    "minimum": 0,
                    "maximum": 1000000000,
                    "multipleOf": 1000
                }
            }
        },
        "risk_profile": {
            "type": "object",
            "title": "Risk Profile Assessment",
            "required": ["investment_objective", "time_horizon", "risk_tolerance"],
            "properties": {
                "investment_objective": {
                    "type": "string",
                    "title": "Primary Investment Objective",
                    "enum": ["capital_preservation", "income", "balanced", "growth", "aggressive_growth"],
                    "default": "balanced"
                },
                "time_horizon": {
                    "type": "string",
                    "title": "Investment Time Horizon",
                    "enum": ["less_than_1_year", "1_to_3_years", "3_to_5_years", "5_to_10_years", "more_than_10_years"],
                    "default": "3_to_5_years"
                },
                "risk_tolerance": {
                    "type": "integer",
                    "title": "Risk Tolerance Level (1-10)",
                    "minimum": 1,
                    "maximum": 10,
                    "default": 5,
                    "description": "1 = Very Conservative, 10 = Very Aggressive"
                },
                "investment_experience_years": {
                    "type": "number",
                    "title": "Years of Investment Experience",
                    "minimum": 0,
                    "maximum": 50,
                    "multipleOf": 0.5,
                    "default": 0
                },
                "portfolio_percentage_stocks": {
                    "type": "number",
                    "title": "Desired % in Stocks",
                    "minimum": 0,
                    "maximum": 100,
                    "multipleOf": 0.01,
                    "default": 30
                },
                "portfolio_percentage_bonds": {
                    "type": "number",
                    "title": "Desired % in Bonds",
                    "minimum": 0,
                    "maximum": 100,
                    "multipleOf": 0.01,
                    "default": 50
                },
                "portfolio_percentage_cash": {
                    "type": "number",
                    "title": "Desired % in Cash/Equivalents",
                    "minimum": 0,
                    "maximum": 100,
                    "multipleOf": 0.01,
                    "default": 20
                }
            }
        },
        "initial_investment": {
            "type": "number",
            "title": "Initial Investment Amount (PHP)",
            "minimum": 10000,
            "maximum": 1000000000,
            "multipleOf": 1000
        },
        "funding_source": {
            "type": "string",
            "title": "Source of Funds",
            "enum": ["salary", "business_income", "inheritance", "investment_income", "savings", "other"],
            "default": "salary"
        },
        "documents": {
            "type": "object",
            "title": "Required Documents",
            "properties": {
                "valid_id": {
                    "type": "string",
                    "title": "Valid ID (File Upload)",
                    "format": "uri",
                    "description": "Upload government-issued ID"
                },
                "proof_of_income": {
                    "type": "string",
                    "title": "Proof of Income (File Upload)",
                    "format": "uri",
                    "description": "Upload ITR, payslip, or business permit"
                },
                "proof_of_billing": {
                    "type": "string",
                    "title": "Proof of Billing (File Upload)",
                    "format": "uri",
                    "description": "Upload utility bill or bank statement"
                }
            }
        },
        "beneficiary_designation": {
            "type": "boolean",
            "title": "Designate Beneficiary",
            "default": False
        },
        "agrees_to_terms": {
            "type": "boolean",
            "title": "I agree to Terms and Conditions",
            "const": True
        }
    },
    "allOf": [
        {
            "if": {
                "properties": {
                    "investor_info": {
                        "properties": {
                            "investor_type": {"const": "corporate"}
                        }
                    }
                }
            },
            "then": {
                "properties": {
                    "investor_info": {
                        "required": ["company_name", "company_tin", "sec_registration"],
                        "properties": {
                            "company_name": {
                                "type": "string",
                                "title": "Company Name",
                                "minLength": 2,
                                "maxLength": 200
                            },
                            "company_tin": {
                                "type": "string",
                                "title": "Company TIN",
                                "pattern": "^[0-9]{9,12}$"
                            },
                            "sec_registration": {
                                "type": "string",
                                "title": "SEC Registration Number",
                                "minLength": 5,
                                "maxLength": 50
                            }
                        }
                    }
                }
            }
        },
        {
            "if": {
                "properties": {
                    "account_type": {
                        "enum": ["uitf", "mutual_fund"]
                    }
                }
            },
            "then": {
                "required": ["fund_selection"],
                "properties": {
                    "fund_selection": {
                        "type": "object",
                        "title": "Fund Selection",
                        "required": ["fund_name", "investment_mode"],
                        "properties": {
                            "fund_name": {
                                "type": "string",
                                "title": "Fund Name",
                                "enum": ["equity_fund", "balanced_fund", "bond_fund", "money_market_fund", "dollar_fund"],
                                "description": "Select investment fund"
                            },
                            "investment_mode": {
                                "type": "string",
                                "title": "Investment Mode",
                                "enum": ["lump_sum", "regular_monthly"],
                                "default": "lump_sum"
                            }
                        }
                    }
                }
            }
        },
        {
            "if": {
                "properties": {
                    "beneficiary_designation": {"const": True}
                }
            },
            "then": {
                "required": ["beneficiaries"],
                "properties": {
                    "beneficiaries": {
                        "type": "array",
                        "title": "Beneficiaries",
                        "minItems": 1,
                        "maxItems": 5,
                        "items": {
                            "type": "object",
                            "required": ["full_name", "relationship", "percentage_share", "date_of_birth"],
                            "properties": {
                                "full_name": {
                                    "type": "string",
                                    "title": "Full Name",
                                    "minLength": 2,
                                    "maxLength": 100
                                },
                                "relationship": {
                                    "type": "string",
                                    "title": "Relationship",
                                    "enum": ["spouse", "child", "parent", "sibling", "relative", "other"]
                                },
                                "date_of_birth": {
                                    "type": "string",
                                    "title": "Date of Birth",
                                    "format": "date"
                                },
                                "percentage_share": {
                                    "type": "number",
                                    "title": "Percentage Share (%)",
                                    "minimum": 0.01,
                                    "maximum": 100,
                                    "multipleOf": 0.01
                                },
                                "contact_number": {
                                    "type": "string",
                                    "title": "Contact Number",
                                    "pattern": "^(\\+63|0)[0-9]{10}$"
                                }
                            }
                        }
                    }
                }
            }
        }
    ],
    "oneOf": [
        {
            "properties": {
                "risk_profile": {
                    "properties": {
                        "risk_tolerance": {"maximum": 3}
                    }
                },
                "account_type": {
                    "enum": ["time_deposit", "bonds", "mutual_fund"]
                }
            }
        },
        {
            "properties": {
                "risk_profile": {
                    "properties": {
                        "risk_tolerance": {"minimum": 4, "maximum": 7}
                    }
                },
                "account_type": {
                    "enum": ["mutual_fund", "uitf", "bonds"]
                }
            }
        },
        {
            "properties": {
                "risk_profile": {
                    "properties": {
                        "risk_tolerance": {"minimum": 8}
                    }
                },
                "account_type": {
                    "enum": ["stocks", "uitf"]
                }
            }
        }
    ]
}


# ============================================================================
# STAGE 4: Database-Backed Form - Personal Loan Application (Security Bank)
# Demonstrates: Database enums, status/substatus, user references, complex validation
# ============================================================================
SECURITY_BANK_PERSONAL_LOAN_TEMPLATE = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Personal Loan Application",
    "description": "Security Bank Personal Loan with database-backed options",
    "type": "object",
    "required": ["loan_purpose", "applicant_details", "loan_details", "employment_details"],
    "properties": {
        "loan_purpose": {
            "type": "string",
            "title": "Loan Purpose",
            "enum": [
                "debt_consolidation",
                "home_improvement",
                "medical_expenses",
                "education",
                "travel",
                "wedding",
                "business_capital",
                "emergency",
                "other"
            ],
            "description": "Primary purpose for the loan"
        },
        "applicant_details": {
            "type": "object",
            "title": "Applicant Details",
            "required": ["first_name", "last_name", "email", "mobile_number", "date_of_birth"],
            "properties": {
                "first_name": {
                    "type": "string",
                    "title": "First Name",
                    "minLength": 1,
                    "maxLength": 50
                },
                "middle_name": {
                    "type": "string",
                    "title": "Middle Name",
                    "maxLength": 50
                },
                "last_name": {
                    "type": "string",
                    "title": "Last Name",
                    "minLength": 1,
                    "maxLength": 50
                },
                "suffix": {
                    "type": "string",
                    "title": "Suffix",
                    "enum": ["", "Jr.", "Sr.", "II", "III", "IV"],
                    "default": ""
                },
                "email": {
                    "type": "string",
                    "title": "Email Address",
                    "format": "email"
                },
                "mobile_number": {
                    "type": "string",
                    "title": "Mobile Number",
                    "pattern": "^(\\+63|0)[0-9]{10}$"
                },
                "landline": {
                    "type": "string",
                    "title": "Landline (Optional)",
                    "pattern": "^(\\+63|0)?[0-9]{7,11}$"
                },
                "date_of_birth": {
                    "type": "string",
                    "title": "Date of Birth",
                    "format": "date",
                    "description": "Must be at least 21 years old"
                },
                "gender": {
                    "type": "string",
                    "title": "Gender",
                    "enum": ["male", "female", "other", "prefer_not_to_say"],
                    "default": "prefer_not_to_say"
                },
                "civil_status": {
                    "type": "string",
                    "title": "Civil Status",
                    "enum": ["single", "married", "widowed", "separated", "divorced"],
                    "default": "single"
                },
                "nationality": {
                    "type": "string",
                    "title": "Nationality",
                    "default": "Filipino",
                    "description": "DB Reference: countries table"
                },
                "residence_address": {
                    "$ref": "#/$defs/address"
                }
            }
        },
        "loan_details": {
            "type": "object",
            "title": "Loan Details",
            "required": ["amount", "term_months", "payment_mode"],
            "properties": {
                "amount": {
                    "type": "number",
                    "title": "Loan Amount (PHP)",
                    "minimum": 20000,
                    "maximum": 2000000,
                    "multipleOf": 1000,
                    "description": "Minimum: ₱20,000 | Maximum: ₱2,000,000"
                },
                "term_months": {
                    "type": "integer",
                    "title": "Loan Term (Months)",
                    "enum": [12, 24, 36, 48, 60],
                    "default": 24,
                    "description": "Repayment period in months"
                },
                "payment_mode": {
                    "type": "string",
                    "title": "Preferred Payment Mode",
                    "enum": ["auto_debit", "over_the_counter", "online_banking", "check"],
                    "default": "auto_debit"
                },
                "promo_code": {
                    "type": "string",
                    "title": "Promo Code (Optional)",
                    "pattern": "^[A-Z0-9]{6,12}$",
                    "description": "Enter promo code if available"
                }
            }
        },
        "employment_details": {
            "type": "object",
            "title": "Employment Details",
            "required": ["employment_type", "employer_name", "industry", "monthly_salary"],
            "properties": {
                "employment_type": {
                    "type": "string",
                    "title": "Employment Type",
                    "enum": ["regular_employed", "contractual", "probationary", "self_employed", "business_owner", "professional", "ofw"],
                    "default": "regular_employed"
                },
                "employer_name": {
                    "type": "string",
                    "title": "Employer/Company Name",
                    "minLength": 2,
                    "maxLength": 200
                },
                "industry": {
                    "type": "string",
                    "title": "Industry",
                    "enum": [
                        "banking_finance",
                        "it_bpo",
                        "healthcare",
                        "education",
                        "manufacturing",
                        "retail",
                        "hospitality",
                        "government",
                        "real_estate",
                        "transportation",
                        "agriculture",
                        "construction",
                        "media",
                        "telecommunications",
                        "other"
                    ],
                    "description": "DB Reference: industries table"
                },
                "position": {
                    "type": "string",
                    "title": "Position/Job Title",
                    "minLength": 2,
                    "maxLength": 100
                },
                "employment_status": {
                    "type": "string",
                    "title": "Employment Status",
                    "enum": ["active", "on_leave", "resigned_pending", "contract_end_pending"],
                    "default": "active",
                    "description": "DB Reference: employment_status table"
                },
                "years_employed": {
                    "type": "number",
                    "title": "Years with Current Employer",
                    "minimum": 0,
                    "maximum": 50,
                    "multipleOf": 0.5
                },
                "monthly_salary": {
                    "type": "number",
                    "title": "Monthly Gross Salary (PHP)",
                    "minimum": 0,
                    "maximum": 100000000,
                    "multipleOf": 0.01
                },
                "other_income": {
                    "type": "number",
                    "title": "Other Monthly Income (PHP)",
                    "minimum": 0,
                    "maximum": 100000000,
                    "multipleOf": 0.01,
                    "default": 0
                },
                "employer_address": {
                    "$ref": "#/$defs/address"
                }
            }
        },
        "references": {
            "type": "array",
            "title": "Personal References",
            "minItems": 2,
            "maxItems": 3,
            "items": {
                "type": "object",
                "required": ["full_name", "relationship", "contact_number"],
                "properties": {
                    "full_name": {
                        "type": "string",
                        "title": "Full Name",
                        "minLength": 2,
                        "maxLength": 100
                    },
                    "relationship": {
                        "type": "string",
                        "title": "Relationship",
                        "enum": ["family", "friend", "colleague", "neighbor"]
                    },
                    "contact_number": {
                        "type": "string",
                        "title": "Contact Number",
                        "pattern": "^(\\+63|0)[0-9]{10}$"
                    },
                    "email": {
                        "type": "string",
                        "title": "Email (Optional)",
                        "format": "email"
                    }
                }
            }
        },
        "existing_loans": {
            "type": "boolean",
            "title": "Do you have existing loans?",
            "default": False
        },
        "data_privacy_consent": {
            "type": "boolean",
            "title": "I consent to data privacy policy",
            "const": True
        },
        "terms_and_conditions": {
            "type": "boolean",
            "title": "I agree to terms and conditions",
            "const": True
        }
    },
    "$defs": {
        "address": {
            "type": "object",
            "title": "Address",
            "required": ["street", "barangay", "city", "province", "zip_code"],
            "properties": {
                "unit_floor": {
                    "type": "string",
                    "title": "Unit/Floor Number",
                    "maxLength": 50
                },
                "building": {
                    "type": "string",
                    "title": "Building Name",
                    "maxLength": 100
                },
                "street": {
                    "type": "string",
                    "title": "Street/Subdivision",
                    "minLength": 1,
                    "maxLength": 200
                },
                "barangay": {
                    "type": "string",
                    "title": "Barangay",
                    "minLength": 1,
                    "maxLength": 100,
                    "description": "DB Reference: barangays table"
                },
                "city": {
                    "type": "string",
                    "title": "City/Municipality",
                    "minLength": 1,
                    "maxLength": 100,
                    "description": "DB Reference: cities table"
                },
                "province": {
                    "type": "string",
                    "title": "Province",
                    "minLength": 1,
                    "maxLength": 100,
                    "description": "DB Reference: provinces table"
                },
                "zip_code": {
                    "type": "string",
                    "title": "ZIP Code",
                    "pattern": "^[0-9]{4}$"
                },
                "country": {
                    "type": "string",
                    "title": "Country",
                    "default": "Philippines"
                }
            }
        }
    },
    "allOf": [
        {
            "if": {
                "properties": {
                    "applicant_details": {
                        "properties": {
                            "civil_status": {"const": "married"}
                        }
                    }
                }
            },
            "then": {
                "properties": {
                    "applicant_details": {
                        "required": ["spouse_details"],
                        "properties": {
                            "spouse_details": {
                                "type": "object",
                                "title": "Spouse Details",
                                "required": ["full_name", "date_of_birth"],
                                "properties": {
                                    "full_name": {
                                        "type": "string",
                                        "title": "Spouse Full Name",
                                        "minLength": 2,
                                        "maxLength": 100
                                    },
                                    "date_of_birth": {
                                        "type": "string",
                                        "title": "Spouse Date of Birth",
                                        "format": "date"
                                    },
                                    "is_employed": {
                                        "type": "boolean",
                                        "title": "Is Spouse Employed?",
                                        "default": False
                                    },
                                    "monthly_income": {
                                        "type": "number",
                                        "title": "Spouse Monthly Income (PHP)",
                                        "minimum": 0,
                                        "multipleOf": 0.01
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        {
            "if": {
                "properties": {
                    "existing_loans": {"const": True}
                }
            },
            "then": {
                "required": ["existing_loans_details"],
                "properties": {
                    "existing_loans_details": {
                        "type": "array",
                        "title": "Existing Loans Details",
                        "minItems": 1,
                        "maxItems": 5,
                        "items": {
                            "type": "object",
                            "required": ["lender", "loan_type", "outstanding_balance", "monthly_amortization"],
                            "properties": {
                                "lender": {
                                    "type": "string",
                                    "title": "Lender/Bank Name",
                                    "minLength": 2,
                                    "maxLength": 100,
                                    "description": "DB Reference: banks table"
                                },
                                "loan_type": {
                                    "type": "string",
                                    "title": "Loan Type",
                                    "enum": ["personal_loan", "auto_loan", "housing_loan", "credit_card", "business_loan", "other"]
                                },
                                "outstanding_balance": {
                                    "type": "number",
                                    "title": "Outstanding Balance (PHP)",
                                    "minimum": 0,
                                    "multipleOf": 0.01
                                },
                                "monthly_amortization": {
                                    "type": "number",
                                    "title": "Monthly Amortization (PHP)",
                                    "minimum": 0,
                                    "multipleOf": 0.01
                                }
                            }
                        }
                    }
                }
            }
        },
        {
            "if": {
                "properties": {
                    "employment_details": {
                        "properties": {
                            "employment_type": {"const": "ofw"}
                        }
                    }
                }
            },
            "then": {
                "properties": {
                    "employment_details": {
                        "required": ["ofw_details"],
                        "properties": {
                            "ofw_details": {
                                "type": "object",
                                "title": "OFW Details",
                                "required": ["country_of_work", "ofw_id_number"],
                                "properties": {
                                    "country_of_work": {
                                        "type": "string",
                                        "title": "Country of Work",
                                        "minLength": 2,
                                        "maxLength": 100,
                                        "description": "DB Reference: countries table"
                                    },
                                    "ofw_id_number": {
                                        "type": "string",
                                        "title": "OFW ID/OWWA Number",
                                        "minLength": 5,
                                        "maxLength": 50
                                    },
                                    "contract_end_date": {
                                        "type": "string",
                                        "title": "Contract End Date",
                                        "format": "date"
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    ]
}


# ============================================================================
# MAIN SEED FUNCTION
# ============================================================================
async def seed_form_templates():
    """Seed form templates for all banks"""
    print("🌱 Starting Form Templates Seeding...")
    
    async with async_session_maker() as db:
        try:
            # Get all banks
            result = await db.execute(select(Bank))
            banks = result.scalars().all()
            
            if not banks:
                print("❌ No banks found. Please seed banks first.")
                return
            
            print(f"✅ Found {len(banks)} banks")
            
            # Map bank codes to templates
            template_mapping = {
                "BPI": {
                    "template": BPI_CREDIT_CARD_TEMPLATE,
                    "name": "Credit Card Application",
                    "version": "1.0.0",
                    "form_type": "credit_card"
                },
                "BDO": {
                    "template": BDO_HOUSING_LOAN_TEMPLATE,
                    "name": "Housing Loan Application",
                    "version": "1.0.0",
                    "form_type": "housing_loan"
                },
                "METRO": {
                    "template": METROBANK_INVESTMENT_TEMPLATE,
                    "name": "Investment Account Opening",
                    "version": "1.0.0",
                    "form_type": "investment"
                },
                "SBC": {
                    "template": SECURITY_BANK_PERSONAL_LOAN_TEMPLATE,
                    "name": "Personal Loan Application",
                    "version": "1.0.0",
                    "form_type": "personal_loan"
                }
            }
            
            created_count = 0
            
            for bank in banks:
                bank_code = bank.code.upper()
                
                if bank_code in template_mapping:
                    mapping = template_mapping[bank_code]
                    
                    # Check if template already exists
                    existing = await db.execute(
                        select(FormTemplate).where(
                            FormTemplate.bank_id == bank.id,
                            FormTemplate.name == mapping["name"],
                            FormTemplate.version == mapping["version"]
                        )
                    )
                    
                    if existing.scalar_one_or_none():
                        print(f"⏭️  Skipping {bank.name} - {mapping['name']} (already exists)")
                        continue
                    
                    # Create template
                    template = FormTemplate(
                        bank_id=bank.id,
                        name=mapping["name"],
                        version=mapping["version"],
                        form_type=mapping["form_type"],
                        schema_json=mapping["template"],
                        ui_schema={
                            "ui:order": ["*"],
                            "ui:submitButtonOptions": {
                                "submitText": "Submit Application",
                                "norender": False,
                                "props": {
                                    "className": "btn btn-primary btn-lg"
                                }
                            }
                        },
                        active=True,
                        description=mapping["template"]["description"]
                    )
                    
                    db.add(template)
                    created_count += 1
                    print(f"✅ Created: {bank.name} - {mapping['name']} v{mapping['version']}")
                else:
                    print(f"⚠️  No template mapping for {bank.name} ({bank_code})")
            
            await db.commit()
            print(f"\n🎉 Seeding completed! Created {created_count} form templates.")
            print("\n📊 Template Summary:")
            print("   • BPI: Credit Card Application (Simple form with basic conditionals)")
            print("   • BDO: Housing Loan Application (Complex nested conditionals)")
            print("   • Metrobank: Investment Account (Advanced: anyOf/oneOf, arrays)")
            print("   • Security Bank: Personal Loan (Database-backed enums)")
            
        except Exception as e:
            await db.rollback()
            print(f"❌ Error seeding templates: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(seed_form_templates())
