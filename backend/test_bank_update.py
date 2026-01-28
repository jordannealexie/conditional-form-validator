#!/usr/bin/env python3
"""
Simple test script to verify bank update functionality
"""
import asyncio
import httpx
import json

BASE_URL = "http://localhost:8000/api/v1"
# You'll need to replace these with valid credentials
TEST_CREDENTIALS = {
    "username": "harrypotter",  # This user exists based on the Casbin logs
    "password": "harrypotter"  # Found in seed_data.py
}

async def test_bank_update():
    async with httpx.AsyncClient() as client:
        print("🔐 Step 1: Authentication")
        
        # Login to get token
        auth_response = await client.post(
            f"{BASE_URL}/auth/token",
            headers={"X-Client-ID": "test-client"},  # Add client ID header
            data={
                "username": TEST_CREDENTIALS["username"],
                "password": TEST_CREDENTIALS["password"]
            }
        )
        
        if auth_response.status_code != 200:
            print(f"❌ Authentication failed: {auth_response.status_code}")
            print(f"Response: {auth_response.text}")
            return
        
        token_data = auth_response.json()
        access_token = token_data["access_token"]
        headers = {
            "Authorization": f"Bearer {access_token}",
            "X-Client-ID": "test-client",
            "Content-Type": "application/json"
        }
        
        print("✅ Authentication successful")
        
        # Step 2: Get all banks to see current state
        print("\n📋 Step 2: Getting current banks list")
        banks_response = await client.get(f"{BASE_URL}/banks/", headers=headers)
        
        if banks_response.status_code != 200:
            print(f"❌ Failed to get banks: {banks_response.status_code}")
            print(f"Response: {banks_response.text}")
            return
        
        banks_data = banks_response.json()
        print(f"✅ Found {len(banks_data.get('data', []))} banks")
        
        # Find a bank to update (use the first one)
        if not banks_data.get('data'):
            print("❌ No banks found to update")
            return
        
        bank_to_update = banks_data['data'][0]
        bank_id = bank_to_update['id']
        original_name = bank_to_update['name']
        original_updated_at = bank_to_update.get('updated_at')
        
        print(f"🎯 Target bank: ID={bank_id}, Name='{original_name}'")
        print(f"📅 Original updated_at: {original_updated_at}")
        
        # Step 3: Update the bank
        print(f"\n✏️  Step 3: Updating bank {bank_id}")
        update_data = {
            "name": f"{original_name}_UPDATED_TEST",
            "description": f"Updated at {asyncio.get_event_loop().time()}"
        }
        
        update_response = await client.put(
            f"{BASE_URL}/banks/{bank_id}",
            headers=headers,
            json=update_data
        )
        
        if update_response.status_code != 200:
            print(f"❌ Failed to update bank: {update_response.status_code}")
            print(f"Response: {update_response.text}")
            return
        
        update_result = update_response.json()
        updated_bank = update_result['data']
        new_updated_at = updated_bank.get('updated_at')
        
        print(f"✅ Update successful!")
        print(f"📝 New name: {updated_bank['name']}")
        print(f"📅 New updated_at: {new_updated_at}")
        
        # Step 4: Verify the update persisted by getting banks list again
        print(f"\n🔍 Step 4: Verifying update persisted")
        verify_response = await client.get(f"{BASE_URL}/banks/", headers=headers)
        
        if verify_response.status_code != 200:
            print(f"❌ Failed to verify update: {verify_response.status_code}")
            return
        
        verify_data = verify_response.json()
        updated_bank_in_list = None
        
        for bank in verify_data['data']:
            if bank['id'] == bank_id:
                updated_bank_in_list = bank
                break
        
        if not updated_bank_in_list:
            print(f"❌ Bank {bank_id} not found in list after update!")
            return
        
        list_updated_at = updated_bank_in_list.get('updated_at')
        list_name = updated_bank_in_list['name']
        
        print(f"🔍 Bank in list - Name: '{list_name}', Updated_at: {list_updated_at}")
        
        # Compare timestamps
        if list_updated_at == new_updated_at and list_name == updated_bank['name']:
            print("🎉 SUCCESS: Update is properly reflected in the list!")
        else:
            print("❌ FAILURE: Update is not properly reflected in the list!")
            print(f"Expected name: '{updated_bank['name']}', Got: '{list_name}'")
            print(f"Expected updated_at: {new_updated_at}, Got: {list_updated_at}")
        
        # Step 5: Restore original name
        print(f"\n🔄 Step 5: Restoring original name")
        restore_data = {"name": original_name}
        
        restore_response = await client.put(
            f"{BASE_URL}/banks/{bank_id}",
            headers=headers,
            json=restore_data
        )
        
        if restore_response.status_code == 200:
            print(f"✅ Bank name restored to '{original_name}'")
        else:
            print(f"⚠️  Failed to restore original name: {restore_response.status_code}")

if __name__ == "__main__":
    print("🧪 Testing Bank Update Functionality\n")
    asyncio.run(test_bank_update())