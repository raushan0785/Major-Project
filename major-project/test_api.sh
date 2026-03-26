#!/usr/bin/env python3
"""Minimal test of the grammar endpoint"""
import subprocess
import sys
import time

# Wait for server
time.sleep(2)

# Use curl to test the endpoint
cmd = '''
curl -s -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}' | \

python3 -c "import sys, json; data = json.load(sys.stdin); print(data.get('access_token', 'NO_TOKEN'))"
'''

try:
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
    token = result.stdout.strip()
    
    if token == 'NO_TOKEN' or not token:
        print("Failed to get token")
        print("stdout:", result.stdout)
        print("stderr:", result.stderr)
        sys.exit(1)
    
    print(f"Token: {token[:30]}...")
    
    # Now test grammar
    filename = '/tmp/grammar_test.json'
    with open(filename, 'w') as f:
        f.write('{"text": "i want to build a app", "num_suggestions": 2}')
    
    curl_cmd = f'curl -s -X POST http://127.0.0.1:8000/grammar/correct -H "Content-Type: application/json" -H "Authorization: Bearer {token}" -d @{filename}'
    
    result2 = subprocess.run(curl_cmd, shell=True, capture_output=True, text=True, timeout=60)
    print("Grammar response:")
    print(result2.stdout[:1000])
    if result2.stderr:
        print("Stderr:", result2.stderr[:500])
        
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
