#!/usr/bin/env python3
import requests
import json

# Test login
print("Testing grammar endpoint...")
login_response = requests.post(
    'http://127.0.0.1:8000/auth/login',
    json={'email': 'test@example.com', 'password': 'password123'},
    timeout=10
)

if login_response.status_code != 200:
    print('✗ Login failed:', login_response.status_code)
    print(login_response.text[:200])
else:
    token = login_response.json().get('access_token')
    print('✓ Login successful, token acquired')
    
    # Test grammar endpoint
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    data = {
        'text': 'i want to build a app for food delivery with login and payment',
        'num_suggestions': 2
    }
    
    print("Sending grammar correction request...")
    response = requests.post(
        'http://127.0.0.1:8000/grammar/correct',
        headers=headers,
        json=data,
        timeout=30
    )
    
    print(f'✓ Grammar API Status: {response.status_code}')
    if response.status_code == 200:
        result = response.json()
        suggestions = result.get('suggestions', [])
        print(f'✓ SUCCESS! Got {len(suggestions)} suggestions')
        for i, sugg in enumerate(suggestions):
            print(f"\n  Option {i+1}:")
            print(f"    Text: {sugg.get('corrected_text', 'N/A')}")
            print(f"    Explanation: {sugg.get('explanation', 'N/A')}")
    else:
        print(f'✗ Error: {response.text[:500]}')
