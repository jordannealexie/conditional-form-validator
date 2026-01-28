#!/usr/bin/env python3
import sys
import os
import requests
import time
import json

# Wait for server to be available
def wait_for_server(max_attempts=30):
    for i in range(max_attempts):
        try:
            response = requests.get("http://localhost:8000/api/v1/health", timeout=1)
            if response.status_code == 200:
                print("✅ Server is ready")
                return True
        except:
            pass
        time.sleep(1)
    return False

def test_complete_flow():
    """Test the complete bank update flow"""
    
    # Check if server is running
    print("🔍 Checking if server is running...")
    if not wait_for_server(5):
        print("❌ Server is not running! Please start it first:")
        print("   cd backend && source venv/bin/activate && uvicorn app.main:app --host 0.0.0.0 --port 8000")
        return False

    # Login
    print("🔑 Authenticating...")
    login_response = requests.post(
        'http://localhost:8000/api/v1/auth/token',
        headers={
            'X-Client-ID': 'test-client',
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        data='username=harrypotter&password=password123'
    )
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.text}")
        return False
        
    token = login_response.json()['data']['access_token']
    print("✅ Authentication successful!")

    # Get current banks
    print("\n📊 Getting current banks...")
    banks_response = requests.get(
        'http://localhost:8000/api/v1/banks/',
        headers={
            'X-Client-ID': 'test-client',
            'Authorization': f'Bearer {token}'
        }
    )
    
    if banks_response.status_code != 200:
        print(f"❌ Failed to get banks: {banks_response.text}")
        return False
        
    banks = banks_response.json()['data']
    bank_1 = next((b for b in banks if b['id'] == 1), None)
    
    if not bank_1:
        print("❌ Bank with ID 1 not found")
        return False
        
    original_name = bank_1['name']
    original_short_name = bank_1['short_name']
    print(f"✅ Found bank 1: '{original_name}' ({original_short_name})")

    # Update the bank
    print("\n🔄 Updating bank...")
    new_name = f"UPDATED BANK {int(time.time())}"
    new_short_name = "UPD"
    
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
        print(f"❌ Update failed: {update_response.text}")
        return False
        
    print(f"✅ Update API call successful")

    # Verify the change persisted
    print("\n🔍 Verifying changes persisted...")
    verify_response = requests.get(
        'http://localhost:8000/api/v1/banks/',
        headers={
            'X-Client-ID': 'test-client',
            'Authorization': f'Bearer {token}'
        }
    )
    
    if verify_response.status_code != 200:
        print(f"❌ Verification failed: {verify_response.text}")
        return False
        
    updated_banks = verify_response.json()['data']
    updated_bank_1 = next((b for b in updated_banks if b['id'] == 1), None)
    
    if not updated_bank_1:
        print("❌ Bank 1 not found after update")
        return False

    print(f"📋 Bank 1 after update: '{updated_bank_1['name']}' ({updated_bank_1['short_name']})")
    
    # Check if changes persisted
    if updated_bank_1['name'] == new_name and updated_bank_1['short_name'] == new_short_name:
        print("\n🎉 SUCCESS! Bank update is working correctly!")
        print(f"   ✓ Name: '{original_name}' → '{new_name}'")
        print(f"   ✓ Short Name: '{original_short_name}' → '{new_short_name}'")
        print("   ✓ Changes are persisted in the database")
        print("   ✓ GET /api/v1/banks/ shows updated data")
        return True
    else:
        print("\n❌ FAILURE! Changes did not persist!")
        print(f"   Expected name: '{new_name}'")
        print(f"   Actual name: '{updated_bank_1['name']}'")
        print(f"   Expected short_name: '{new_short_name}'")
        print(f"   Actual short_name: '{updated_bank_1['short_name']}'")
        return False

if __name__ == "__main__":
    print("🧪 Bank Update Integration Test")
    print("=" * 50)
    
    success = test_complete_flow()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ ALL TESTS PASSED! The bank update functionality is working correctly.")
        sys.exit(0)
    else:
        print("❌ TESTS FAILED! Bank update functionality needs attention.")
        sys.exit(1)