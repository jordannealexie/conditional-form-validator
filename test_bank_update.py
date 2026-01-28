#!/usr/bin/env python3
import requests
import json
import subprocess
import time
import signal
import os

# Start the server in background
print("Starting server...")
server_process = subprocess.Popen(
    ["python", "-m", "uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"],
    cwd="/home/adrian/conditional-form-validator-backend2/conditional-form-validator-backend",
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)

# Wait for server to start
time.sleep(8)

try:
    # Get token
    print("Getting auth token...")
    login_response = requests.post(
        'http://localhost:8000/api/v1/auth/token',
        headers={'X-Client-ID': 'test-client', 'Content-Type': 'application/x-www-form-urlencoded'},
        data='username=harrypotter&password=password123'
    )

    if login_response.status_code == 200:
        token = login_response.json()['data']['access_token']
        print('✅ Got token')
        
        # Test bank update
        print("Testing bank update...")
        update_response = requests.put(
            'http://localhost:8000/api/v1/banks/1',
            headers={
                'X-Client-ID': 'test-client',
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {token}'
            },
            json={'name': 'Test Bank UPDATE WORKING', 'short_name': 'TBW'}
        )
        
        print(f'Update status: {update_response.status_code}')
        if update_response.status_code == 200:
            print('Update response:', json.dumps(update_response.json(), indent=2))
            
            # Wait a moment for changes to settle
            time.sleep(1)
            
            # Now test GET to see if update persisted
            print("Testing GET to verify persistence...")
            get_response = requests.get(
                'http://localhost:8000/api/v1/banks/',
                headers={
                    'X-Client-ID': 'test-client',
                    'Authorization': f'Bearer {token}'
                }
            )
            
            print(f'GET status: {get_response.status_code}')
            if get_response.status_code == 200:
                banks = get_response.json()['data']
                bank_1 = next((b for b in banks if b['id'] == 1), None)
                if bank_1:
                    print(f'Bank 1 name: {bank_1["name"]}, short_name: {bank_1["short_name"]}')
                    if bank_1['name'] == 'Test Bank UPDATE WORKING':
                        print('✅ UPDATE SUCCESSFUL! Changes are persisted!')
                    else:
                        print('❌ Update failed - old values still present')
                        print(f'Expected: "Test Bank UPDATE WORKING", Got: "{bank_1["name"]}"')
                else:
                    print('❌ Bank 1 not found')
            else:
                print(f'❌ GET request failed: {get_response.text}')
        else:
            print(f'❌ Update failed: {update_response.text}')
    else:
        print(f'❌ Login failed: {login_response.text}')

finally:
    # Stop the server
    print("Stopping server...")
    server_process.send_signal(signal.SIGTERM)
    time.sleep(2)
    if server_process.poll() is None:
        server_process.kill()
    print("Server stopped.")