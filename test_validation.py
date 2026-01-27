#!/usr/bin/env python3
"""
Test script for enhanced field validation functionality.
Tests the new field-level validation features added to the FormValidator.
"""
import sys
import os
sys.path.append('backend')

from app.core.validator import FormValidator

def test_field_validation():
    """Test various field validation scenarios."""
    
    print("🧪 Testing Enhanced Field Validation System")
    print("=" * 50)
    
    # Test 1: Email validation
    print("\n📧 Test 1: Email Validation")
    test_data = {'email': 'invalid@email'}
    test_fields = [{'id': 'email', 'type': 'email', 'label': 'Email Address', 'required': True}]
    result = FormValidator.validate(test_data, {'fields': test_fields})
    print(f"Invalid email validation: {'✅ PASS' if not result['valid'] and any('email' in e['message'].lower() for e in result['errors']) else '❌ FAIL'}")
    
    # Test 2: Phone validation
    print("\n📞 Test 2: Phone Validation")
    test_data = {'phone': '123'}  # Invalid phone
    test_fields = [{'id': 'phone', 'type': 'phone', 'label': 'Phone Number', 'required': True}]
    result = FormValidator.validate(test_data, {'fields': test_fields})
    print(f"Invalid phone validation: {'✅ PASS' if not result['valid'] and any('phone' in e['message'].lower() for e in result['errors']) else '❌ FAIL'}")
    
    # Test 3: Currency validation
    print("\n💰 Test 3: Currency Validation")
    test_data = {'price': -50}  # Negative currency
    test_fields = [{'id': 'price', 'type': 'currency', 'label': 'Price', 'required': True}]
    result = FormValidator.validate(test_data, {'fields': test_fields})
    print(f"Negative currency validation: {'✅ PASS' if not result['valid'] and any('negative' in e['message'].lower() for e in result['errors']) else '❌ FAIL'}")
    
    # Test 4: Percentage validation
    print("\n📊 Test 4: Percentage Validation")
    test_data = {'completion': 150}  # Over 100%
    test_fields = [{'id': 'completion', 'type': 'percentage', 'label': 'Completion', 'required': True}]
    result = FormValidator.validate(test_data, {'fields': test_fields})
    print(f"Over 100% validation: {'✅ PASS' if not result['valid'] and any('100' in e['message'] for e in result['errors']) else '❌ FAIL'}")
    
    # Test 5: String length validation
    print("\n📝 Test 5: String Length Validation")
    test_data = {'description': 'Hi'}  # Too short
    test_fields = [{
        'id': 'description', 
        'type': 'text', 
        'label': 'Description', 
        'required': True,
        'validation': {'minLength': 10}
    }]
    result = FormValidator.validate(test_data, {'fields': test_fields})
    print(f"Min length validation: {'✅ PASS' if not result['valid'] and any('characters long' in e['message'] for e in result['errors']) else '❌ FAIL'}")
    
    # Test 6: Select options validation
    print("\n🎯 Test 6: Select Options Validation")
    test_data = {'status': 'invalid_option'}
    test_fields = [{
        'id': 'status', 
        'type': 'select', 
        'label': 'Status', 
        'required': True,
        'options': ['active', 'inactive', 'pending']
    }]
    result = FormValidator.validate(test_data, {'fields': test_fields})
    print(f"Invalid option validation: {'✅ PASS' if not result['valid'] and any('allowed options' in e['message'] for e in result['errors']) else '❌ FAIL'}")
    
    # Test 7: Conditional field validation
    print("\n🔄 Test 7: Conditional Field Validation")
    test_data = {'employment_status': 'employed', 'company': ''}  # Required when employed
    test_fields = [
        {'id': 'employment_status', 'type': 'select', 'label': 'Employment Status', 'required': True, 'options': ['employed', 'unemployed']},
        {'id': 'company', 'type': 'text', 'label': 'Company', 'required': True, 'show_if': {'field': 'employment_status', 'operator': 'equals', 'value': 'employed'}}
    ]
    result = FormValidator.validate(test_data, {'fields': test_fields})
    print(f"Conditional required validation: {'✅ PASS' if not result['valid'] and any(e['field'] == 'company' for e in result['errors']) else '❌ FAIL'}")
    
    # Test 8: Valid data should pass
    print("\n✅ Test 8: Valid Data Should Pass")
    test_data = {
        'email': 'user@example.com',
        'phone': '09650044464',  # Valid Philippines phone
        'price': 99.99,
        'completion': 85,
        'description': 'This is a valid description that meets the minimum length requirement'
    }
    test_fields = [
        {'id': 'email', 'type': 'email', 'label': 'Email', 'required': True},
        {'id': 'phone', 'type': 'phone', 'label': 'Phone', 'required': True},
        {'id': 'price', 'type': 'currency', 'label': 'Price', 'required': True},
        {'id': 'completion', 'type': 'percentage', 'label': 'Completion', 'required': True},
        {'id': 'description', 'type': 'text', 'label': 'Description', 'required': True, 'validation': {'minLength': 10}}
    ]
    result = FormValidator.validate(test_data, {'fields': test_fields})
    print(f"Valid data passes: {'✅ PASS' if result['valid'] else '❌ FAIL'}")
    if not result['valid']:
        print("Unexpected errors:", result['errors'])
    
    print("\n" + "=" * 50)
    print("🎉 Field Validation Test Suite Complete!")

if __name__ == "__main__":
    test_field_validation()