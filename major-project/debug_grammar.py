#!/usr/bin/env python3
"""Test the grammar endpoint"""
import requests
import json
import sys

def main():
    try:
        # Login
        print("Step 1: Logging in...", file=sys.stderr)
        login_resp = requests.post(
            'http://127.0.0.1:8000/auth/login',
            json={'email': 'test@example.com', 'password': 'password123'},
            timeout=10
        )
        
        if login_resp.status_code != 200:
            print(f"FAIL: Login failed with status {login_resp.status_code}", file=sys.stderr)
            print(login_resp.text, file=sys.stderr)
            return 1
        
        token = login_resp.json()['access_token']
        print(f"OK: Got token", file=sys.stderr)
        
        # Test grammar
        print("Step 2: Testing grammar endpoint...", file=sys.stderr)
        headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'}
        data = {'text': 'i want to build a healthcare app where doctor and patient can communicate', 'num_suggestions': 2}
        
        response = requests.post(
            'http://127.0.0.1:8000/grammar/correct',
            headers=headers,
            json=data,
            timeout=60
        )
        
        print(f"Status: {response.status_code}", file=sys.stderr)
        
        if response.status_code == 200:
            result = response.json()
            print(f"OK: Got {len(result.get('suggestions', []))} suggestions", file=sys.stderr)
            # Print full response
            print(json.dumps(result, indent=2))
        else:
            print(f"FAIL: API returned {response.status_code}", file=sys.stderr)
            print(f"Response: {response.text}", file=sys.stderr)
            return 1
            
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
