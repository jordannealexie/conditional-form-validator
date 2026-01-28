#!/usr/bin/env python3
import requests
import json
import sys

def test_bank_update():
    """Test bank update functionality to ensure changes persist"""
    
    # Get authentication token
    print("🔑 Getting authentication token...")
    try:
        login_response = requests.post(
            'http://localhost:8000/api/v1/auth/token',
            headers={
                'X-Client-ID': 'test-client',
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            data='username=harrypotter&password=password123'
        )
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            print(f"Response: {login_response.text}")
            return False
            
        token = login_response.json()['data']['access_token']
        print("✅ Authentication successful!")
        
    except Exception as e:
        print(f"❌ Login error: {e}")
        return False

    # Test 1: Get current bank state
    print("\n📊 Getting current bank state...")
    try:
        get_response = requests.get(
            'http://localhost:8000/api/v1/banks/',
            headers={
                'X-Client-ID': 'test-client',
                'Authorization': f'Bearer {token}'
            }
        )
        
        if get_response.status_code != 200:
            print(f"❌ GET banks failed: {get_response.status_code}")
            print(f"Response: {get_response.text}")
            return False
            
        banks = get_response.json()['data']
        bank_1 = next((b for b in banks if b['id'] == 1), None)
        
        if not bank_1:
            print("❌ Bank with ID 1 not found")
            return False
            
        original_name = bank_1['name']
        print(f"✅ Current bank 1: name='{original_name}', short_name='{bank_1['short_name']}'")
        
    except Exception as e:
        print(f"❌ GET banks error: {e}")
        return False

    # Test 2: Update the bank
    print("\n🔄 Testing bank update...")
    try:
        new_name = f"Updated Bank Test {int(requests.get('http://localhost:8000/api/v1/health').elapsed.total_seconds() * 1000)}"
        new_short_name = "UBT"
        
        update_response = requests.put(
            'http://localhost:8000/api/v1/banks/1',
            headers={
                'X-Client-ID': 'test-client',
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {token}'
            },
            json={
                'name': new_name,
                'short_name': new_short_name
            }
        )
        
        if update_response.status_code != 200:
            print(f"❌ PUT bank failed: {update_response.status_code}")
            print(f"Response: {update_response.text}")
            return False
            
        updated_bank = update_response.json()['data']
        print(f"✅ Bank update successful!")
        print(f"   Response: name='{updated_bank['name']}', short_name='{updated_bank['short_name']}'")
        
    except Exception as e:
        print(f"❌ PUT bank error: {e}")
        return False

    # Test 3: Verify changes persisted with GET
    print("\n🔍 Verifying changes persisted...")
    try:
        verify_response = requests.get(
            'http://localhost:8000/api/v1/banks/',
            headers={
                'X-Client-ID': 'test-client',
                'Authorization': f'Bearer {token}'
            }
        )
        
        if verify_response.status_code != 200:
            print(f"❌ Verification GET failed: {verify_response.status_code}")
            print(f"Response: {verify_response.text}")
            return False
            
        banks = verify_response.json()['data']
        updated_bank_1 = next((b for b in banks if b['id'] == 1), None)
        
        if not updated_bank_1:
            print("❌ Bank 1 not found in verification GET")
            return False
            
        print(f"📋 Current state: name='{updated_bank_1['name']}', short_name='{updated_bank_1['short_name']}'")
        
        # Check if changes persisted
        if updated_bank_1['name'] == new_name and updated_bank_1['short_name'] == new_short_name:
            print("✅ SUCCESS! Bank update changes are properly persisted!")
            print(f"   ✓ Name updated: '{original_name}' → '{new_name}'")
            print(f"   ✓ Short name updated: → '{new_short_name}'")
            return True
        else:
            print("❌ FAILURE! Changes did not persist!")
            print(f"   Expected name: '{new_name}', Got: '{updated_bank_1['name']}'")
            print(f"   Expected short_name: '{new_short_name}', Got: '{updated_bank_1['short_name']}'")
            return False
            
    except Exception as e:
        print(f"❌ Verification error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Bank Update Functionality")
    print("=" * 50)
    
    success = test_bank_update()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 ALL TESTS PASSED! Bank update functionality is working correctly!")
        sys.exit(0)
    else:
        print("💥 TESTS FAILED! Bank update functionality needs fixing!")
        sys.exit(1)