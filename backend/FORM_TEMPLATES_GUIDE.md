# Form Templates Implementation Guide

## Overview
This guide explains the sample form templates created for each bank, demonstrating JSON Schema Draft-07 compliance, nested conditionals, various field types, and how caching solves N+1 query problems.

---

## 🎯 Development Stages

### Stage 1: Simple Forms (BPI Credit Card)
**File:** `scripts/seed_form_templates.py` → `BPI_CREDIT_CARD_TEMPLATE`

**Features Demonstrated:**
- ✅ Basic JSON Schema types: `string`, `number`, `boolean`
- ✅ Simple `if/then/else` conditionals
- ✅ `enum` for dropdown selections
- ✅ Default values
- ✅ Pattern validation (phone, email)
- ✅ Min/max constraints

**Example Conditional Logic:**
```json
{
  "if": {
    "properties": {
      "applicant_type": {"const": "corporate"}
    }
  },
  "then": {
    "required": ["company_name", "company_tin"],
    "properties": {
      "company_name": {"type": "string"},
      "company_tin": {"type": "string"}
    }
  },
  "else": {
    "required": ["date_of_birth"],
    "properties": {
      "date_of_birth": {"type": "string", "format": "date"}
    }
  }
}
```

**Field Types Used:**
- `string` with pattern validation (phone, email)
- `number` with min/max/multipleOf (currency)
- `enum` (applicant type, card type, employment status)

---

### Stage 2: Complex Forms (BDO Housing Loan)
**File:** `scripts/seed_form_templates.py` → `BDO_HOUSING_LOAN_TEMPLATE`

**Features Demonstrated:**
- ✅ Nested object structures (applicant_info, property_info)
- ✅ Multiple `allOf` conditionals
- ✅ Complex address type (non-string composite object)
- ✅ Integer types with constraints
- ✅ Float numbers with multipleOf for decimals
- ✅ Nested conditionals (citizenship → work permit, civil status → spouse)

**Example Nested Conditionals:**
```json
{
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
              "work_permit_number": {"type": "string"}
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
            "required": ["current_lender", "outstanding_balance"]
          }
        }
      }
    }
  ]
}
```

**Address Type (Composite Object):**
```json
{
  "property_address": {
    "type": "object",
    "required": ["street", "barangay", "city", "province", "zip_code"],
    "properties": {
      "street": {"type": "string"},
      "barangay": {"type": "string"},
      "city": {"type": "string"},
      "province": {"type": "string"},
      "zip_code": {"type": "string", "pattern": "^[0-9]{4}$"},
      "country": {"type": "string", "default": "Philippines"}
    }
  }
}
```

---

### Stage 3: Advanced Forms (Metrobank Investment)
**File:** `scripts/seed_form_templates.py` → `METROBANK_INVESTMENT_TEMPLATE`

**Features Demonstrated:**
- ✅ `oneOf` validation (risk tolerance → account type matching)
- ✅ `anyOf` logic
- ✅ Array types with minItems/maxItems (beneficiaries)
- ✅ Percentage type (0-100 with multipleOf 0.01)
- ✅ Rating type (1-10 integer scale)
- ✅ File upload (format: "uri")
- ✅ Boolean toggles (beneficiary_designation)

**oneOf Example (Risk-Based Account Validation):**
```json
{
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
```

**Array of Objects (Beneficiaries):**
```json
{
  "beneficiaries": {
    "type": "array",
    "minItems": 1,
    "maxItems": 5,
    "items": {
      "type": "object",
      "required": ["full_name", "relationship", "percentage_share"],
      "properties": {
        "full_name": {"type": "string"},
        "relationship": {
          "type": "string",
          "enum": ["spouse", "child", "parent", "sibling"]
        },
        "percentage_share": {
          "type": "number",
          "minimum": 0.01,
          "maximum": 100,
          "multipleOf": 0.01
        }
      }
    }
  }
}
```

**Field Types Used:**
- Rating: `integer` with min=1, max=10
- Percentage: `number` with min=0, max=100, multipleOf=0.01
- Currency: `number` with multipleOf=1000
- File: `string` with format="uri"

---

### Stage 4: Database-Backed Forms (Security Bank Personal Loan)
**File:** `scripts/seed_form_templates.py` → `SECURITY_BANK_PERSONAL_LOAN_TEMPLATE`

**Features Demonstrated:**
- ✅ `$ref` for reusable schemas (address definition)
- ✅ Database table references (noted in description)
- ✅ Status/substatus enums (employment_status)
- ✅ Multiple nested conditionals (married → spouse, existing loans → details)
- ✅ Array of references (personal references, existing loans)

**$ref Usage (Reusable Address Schema):**
```json
{
  "$defs": {
    "address": {
      "type": "object",
      "required": ["street", "barangay", "city", "province", "zip_code"],
      "properties": {
        "street": {"type": "string"},
        "barangay": {
          "type": "string",
          "description": "DB Reference: barangays table"
        },
        "city": {
          "type": "string",
          "description": "DB Reference: cities table"
        }
      }
    }
  },
  "properties": {
    "residence_address": {"$ref": "#/$defs/address"},
    "employer_address": {"$ref": "#/$defs/address"}
  }
}
```

**Database-Backed Enums:**
```json
{
  "nationality": {
    "type": "string",
    "default": "Filipino",
    "description": "DB Reference: countries table"
  },
  "industry": {
    "type": "string",
    "enum": ["banking_finance", "it_bpo", "healthcare"],
    "description": "DB Reference: industries table"
  },
  "employment_status": {
    "type": "string",
    "enum": ["active", "on_leave", "resigned_pending"],
    "default": "active",
    "description": "DB Reference: employment_status table"
  }
}
```

---

## 🚀 N+1 Query Problem & Caching Solution

### The Problem
Without caching, each form submission validation requires:
1. Query to fetch form template
2. Query to fetch bank details (via relationship)
3. If multiple submissions → N+1 queries

**Example:**
```python
# BAD: N+1 queries for 100 submissions
for submission in submissions:
    template = await db.get(FormTemplate, submission.template_id)  # Query 1, 2, 3...
    bank = template.bank  # Additional query per template
    validate(template.schema_json, submission.data)
```

### The Solution: Template Cache
**File:** `app/core/cache.py`

```python
from app.core.cache import template_cache

# GOOD: Single query, cached for 1 hour
template = await template_cache.get(
    key=f"template:{template_id}",
    fetch_func=lambda: repository.get_with_bank(template_id)
)
```

**Repository with Eager Loading:**
**File:** `app/repositories/forms.py`

```python
async def get_with_bank(self, template_id: int) -> Optional[FormTemplate]:
    """Get template with bank relationship (prevents N+1)"""
    
    # Check cache first
    cached = self._from_cache(template_id)
    if cached:
        return cached
    
    # Single query with joinedload (no N+1)
    result = await self.db.execute(
        select(FormTemplate)
        .options(joinedload(FormTemplate.bank))  # Eager load bank
        .where(FormTemplate.id == template_id)
    )
    
    template = result.scalar_one_or_none()
    
    # Cache for 1 hour
    if template:
        self._cache_template(template)
    
    return template
```

### Performance Improvement
- **Before:** 100 submissions = 200+ queries (100 template + 100 bank)
- **After:** 100 submissions = 1 query (first fetch) + 99 cache hits
- **Improvement:** ~99.5% reduction in database load

---

## 📊 Field Type Reference

### Primitive Types
```json
{
  "string_field": {"type": "string"},
  "number_field": {"type": "number"},
  "integer_field": {"type": "integer"},
  "boolean_field": {"type": "boolean"},
  "null_field": {"type": "null"},
  "array_field": {"type": "array"}
}
```

### Predefined Data Types

#### Text Field
```json
{
  "type": "string",
  "minLength": 1,
  "maxLength": 100,
  "pattern": "^[a-zA-Z\\s]+$"
}
```

#### Long Text
```json
{
  "type": "string",
  "minLength": 1,
  "maxLength": 5000
}
```

#### Email
```json
{
  "type": "string",
  "format": "email"
}
```

#### Phone Number
```json
{
  "type": "string",
  "pattern": "^(\\+63|0)[0-9]{10}$"
}
```

#### Password
```json
{
  "type": "string",
  "minLength": 8,
  "pattern": "^(?=.*[a-z])(?=.*[A-Z])(?=.*\\d)(?=.*[@$!%*?&])[A-Za-z\\d@$!%*?&]"
}
```

#### Number (Generic)
```json
{
  "type": "number",
  "minimum": 0,
  "maximum": 1000000
}
```

#### Integer
```json
{
  "type": "integer",
  "minimum": 1,
  "maximum": 100
}
```

#### Currency (PHP)
```json
{
  "type": "number",
  "minimum": 0,
  "multipleOf": 0.01,
  "description": "Amount in Philippine Peso"
}
```

#### Percentage
```json
{
  "type": "number",
  "minimum": 0,
  "maximum": 100,
  "multipleOf": 0.01
}
```

#### Date
```json
{
  "type": "string",
  "format": "date"
}
```

#### DateTime
```json
{
  "type": "string",
  "format": "date-time"
}
```

#### Boolean
```json
{
  "type": "boolean",
  "default": false
}
```

#### Enum (Dropdown)
```json
{
  "type": "string",
  "enum": ["option1", "option2", "option3"],
  "default": "option1"
}
```

#### File Upload
```json
{
  "type": "string",
  "format": "uri",
  "description": "Upload file"
}
```

#### Rating (1-5 stars)
```json
{
  "type": "integer",
  "minimum": 1,
  "maximum": 5,
  "default": 3
}
```

#### URL
```json
{
  "type": "string",
  "format": "uri",
  "pattern": "^https?://"
}
```

#### JSON Field
```json
{
  "type": "object",
  "additionalProperties": true
}
```

#### Address (Composite Object)
```json
{
  "type": "object",
  "required": ["street", "city", "zip_code"],
  "properties": {
    "street": {"type": "string"},
    "barangay": {"type": "string"},
    "city": {"type": "string"},
    "province": {"type": "string"},
    "zip_code": {"type": "string", "pattern": "^[0-9]{4}$"}
  }
}
```

---

## 🎨 Conditional Logic Patterns

### 1. Simple If/Then/Else
```json
{
  "if": {"properties": {"type": {"const": "individual"}}},
  "then": {"required": ["ssn"]},
  "else": {"required": ["tin"]}
}
```

### 2. AllOf (Multiple Conditions)
```json
{
  "allOf": [
    {
      "if": {"properties": {"married": {"const": true}}},
      "then": {"required": ["spouse_name"]}
    },
    {
      "if": {"properties": {"has_kids": {"const": true}}},
      "then": {"required": ["num_children"]}
    }
  ]
}
```

### 3. AnyOf (At Least One)
```json
{
  "anyOf": [
    {"required": ["email"]},
    {"required": ["phone"]},
    {"required": ["address"]}
  ]
}
```

### 4. OneOf (Exactly One)
```json
{
  "oneOf": [
    {
      "properties": {
        "payment_method": {"const": "card"},
        "card_number": {"type": "string"}
      },
      "required": ["card_number"]
    },
    {
      "properties": {
        "payment_method": {"const": "bank"},
        "account_number": {"type": "string"}
      },
      "required": ["account_number"]
    }
  ]
}
```

### 5. Not (Exclusion)
```json
{
  "not": {
    "properties": {
      "age": {"maximum": 18}
    }
  }
}
```

### 6. Nested Conditionals
```json
{
  "if": {
    "properties": {"employment_type": {"const": "employed"}}
  },
  "then": {
    "required": ["employer"],
    "properties": {
      "employer": {
        "type": "object",
        "required": ["name"],
        "properties": {
          "name": {"type": "string"},
          "years": {"type": "number"}
        }
      }
    },
    "if": {
      "properties": {"employer": {"properties": {"years": {"minimum": 5}}}}
    },
    "then": {
      "properties": {
        "employer": {
          "required": ["manager_reference"]
        }
      }
    }
  }
}
```

---

## 🗄️ Database Integration Patterns

### 1. Enum Table Reference
```sql
CREATE TABLE employment_status (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    label VARCHAR(100) NOT NULL,
    active BOOLEAN DEFAULT true
);

INSERT INTO employment_status (code, label) VALUES
    ('active', 'Active Employment'),
    ('on_leave', 'On Leave'),
    ('resigned_pending', 'Resignation Pending');
```

**JSON Schema:**
```json
{
  "employment_status": {
    "type": "string",
    "enum": ["active", "on_leave", "resigned_pending"],
    "description": "DB Reference: employment_status table"
  }
}
```

### 2. Dynamic Options (API Endpoint)
```python
@router.get("/api/v1/options/industries")
async def get_industries(db: AsyncSession = Depends(get_db)):
    """Get dynamic industry options from database"""
    result = await db.execute(select(Industry).where(Industry.active == True))
    industries = result.scalars().all()
    return [{"value": i.code, "label": i.name} for i in industries]
```

**Frontend Integration:**
```javascript
// Fetch dynamic options
const industries = await fetch('/api/v1/options/industries').then(r => r.json());

// Update enum in schema dynamically
schema.properties.industry.enum = industries.map(i => i.value);
```

### 3. Cascading Selects (Province → City → Barangay)
```python
@router.get("/api/v1/options/cities")
async def get_cities(province_id: int, db: AsyncSession = Depends(get_db)):
    """Get cities filtered by province"""
    result = await db.execute(
        select(City)
        .where(City.province_id == province_id, City.active == True)
    )
    return result.scalars().all()
```

---

## 🏃 Running the Seed Script

```bash
cd /home/vboxuser/conditional-form-validator-backend/backend

# Activate virtual environment
source venv/bin/activate

# Run seed script
python scripts/seed_form_templates.py
```

**Expected Output:**
```
🌱 Starting Form Templates Seeding...
✅ Found 4 banks
✅ Created: BPI - Credit Card Application v1.0.0
✅ Created: BDO Unibank - Housing Loan Application v1.0.0
✅ Created: Metrobank - Investment Account Opening v1.0.0
✅ Created: Security Bank - Personal Loan Application v1.0.0

🎉 Seeding completed! Created 4 form templates.

📊 Template Summary:
   • BPI: Credit Card Application (Simple form with basic conditionals)
   • BDO: Housing Loan Application (Complex nested conditionals)
   • Metrobank: Investment Account (Advanced: anyOf/oneOf, arrays)
   • Security Bank: Personal Loan (Database-backed enums)
```

---

## 📚 Additional Resources

- [JSON Schema Official Docs](https://json-schema.org/)
- [Understanding JSON Schema](https://json-schema.org/understanding-json-schema/)
- [JSON Schema Conditionals](https://json-schema.org/understanding-json-schema/reference/conditionals)
- [Structuring Complex Schemas](https://json-schema.org/understanding-json-schema/structuring)
- [Draft-07 Specification](https://json-schema.org/draft-07/json-schema-release-notes.html)

---

## ✅ Validation Checklist

- [x] JSON Schema Draft-07 compliant
- [x] Nested conditional logic (if/then/else, allOf)
- [x] All primitive types (string, number, integer, boolean, array, object)
- [x] Predefined data types (email, phone, date, currency, percentage)
- [x] Complex types (address, rating, file upload)
- [x] Default values
- [x] Pattern validation (regex)
- [x] Min/max constraints
- [x] Enum support
- [x] Array validation (minItems, maxItems)
- [x] Database-backed options
- [x] Reusable schemas ($ref, $defs)
- [x] Caching layer (N+1 prevention)
- [x] Eager loading (joinedload)

