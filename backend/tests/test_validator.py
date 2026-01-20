import pytest
from app.core.validator import FormValidator

def test_basic_validation():
    schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "number"}
        },
        "required": ["name"]
    }
    template = {"json_schema": schema, "fields": []}
    
    # Valid
    res = FormValidator.validate({"name": "John", "age": 30}, template)
    assert res["valid"] is True
    
    # Invalid missing required
    res = FormValidator.validate({"age": 30}, template)
    assert res["valid"] is False
    assert any(e["field"] == "name" for e in res["errors"])

def test_conditional_logic():
    fields = [
        {
            "id": "employment_status",
            "type": "select",
            "options": ["Employed", "Unemployed"],
            "label": "Employment Status"
        },
        {
            "id": "employer_name",
            "type": "text",
            "required": True,
            "label": "Employer Name",
            "show_if": {"field": "employment_status", "operator": "equals", "value": "Employed"}
        }
    ]
    template = {"json_schema": {}, "fields": fields}
    
    # Unemployed - employer_name not required
    res = FormValidator.validate({"employment_status": "Unemployed"}, template)
    assert res["valid"] is True
    
    # Employed - employer_name required but missing
    res = FormValidator.validate({"employment_status": "Employed"}, template)
    assert res["valid"] is False
    assert any(e["field"] == "employer_name" for e in res["errors"])
    
    # Employed - employer_name present
    res = FormValidator.validate({"employment_status": "Employed", "employer_name": "Acme"}, template)
    assert res["valid"] is True

def test_nested_conditional_logic():
    fields = [
        {"id": "loan_amount", "type": "number", "label": "Loan Amount"},
        {
            "id": "collateral_required",
            "type": "checkbox",
            "label": "Collateral Required",
            "show_if": {"field": "loan_amount", "operator": "greater_than", "value": 500000}
        },
        {
            "id": "collateral_type",
            "type": "text",
            "required": True,
            "label": "Collateral Type",
            "show_if": {
                "all": [
                    {"field": "loan_amount", "operator": "greater_than", "value": 500000},
                    {"field": "collateral_required", "operator": "equals", "value": True}
                ]
            }
        }
    ]
    template = {"json_schema": {}, "fields": fields}
    
    # Low loan
    res = FormValidator.validate({"loan_amount": 100000}, template)
    assert res["valid"] is True
    
    # High loan, collateral not checked
    res = FormValidator.validate({"loan_amount": 1000000, "collateral_required": False}, template)
    assert res["valid"] is True
    
    # High loan, collateral checked, type missing
    res = FormValidator.validate({"loan_amount": 1000000, "collateral_required": True}, template)
    assert res["valid"] is False
    assert any(e["field"] == "collateral_type" for e in res["errors"])
    
    # High loan, collateral checked, type present
    res = FormValidator.validate({
        "loan_amount": 1000000, 
        "collateral_required": True,
        "collateral_type": "Property"
    }, template)
    assert res["valid"] is True
