#!/usr/bin/env python3
import requests
import json
import time

time.sleep(2)  # Wait for server to reload

# Test login
login_resp = requests.post('http://127.0.0.1:8000/auth/login', 
    json={'email': 'test@example.com', 'password': 'password123'},
    timeout=10)

print(f"Login status: {login_resp.status_code}")

if login_resp.status_code == 200:
    token = login_resp.json()['access_token']
    print('✓ Login successful')
    
    # Test grammar endpoint
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    data = {
        'text': 'i want to build a healthcare app where doctor and patient can communicate',
        'num_suggestions': 2
    }
    
    print("Calling grammar/correct endpoint...")
    gramm_resp = requests.post('http://127.0.0.1:8000/grammar/correct',
        headers=headers, json=data, timeout=60)
    
    print(f'Grammar Status: {gramm_resp.status_code}')
    print(f'Response: {gramm_resp.text}')
else:
    print(f'Login failed: {login_resp.status_code}')
    print(f'Error: {login_resp.text}')
