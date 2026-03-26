import asyncio
import requests

async def test_grammar():
    # Wait for server to be ready
    import time
    time.sleep(1)
    
    try:
        # Login first
        login_resp = requests.post(
            'http://127.0.0.1:8000/auth/login',
            json={'email': 'test@example.com', 'password': 'password123'},
            timeout=10
        )
        
        if login_resp.status_code != 200:
            print(f"Login failed: {login_resp.status_code}")
            print(login_resp.text)
            return
        
        token = login_resp.json()['access_token']
        print("✓ Login successful")
        
        # Now test grammar
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        }
        
        text = "i want to build a healthcare system where doctor and patient can communicate easily"
        data = {'text': text, 'num_suggestions': 2}
        
        print(f"Testing grammar with text: {text[:50]}...")
        
        grammar_resp = requests.post(
            'http://127.0.0.1:8000/grammar/correct',
            headers=headers,
            json=data,
            timeout=60
        )
        
        print(f"Status: {grammar_resp.status_code}")
        
        if grammar_resp.status_code == 200:
            result = grammar_resp.json()
            print("✓ SUCCESS!")
            print(f"Suggestions: {len(result.get('suggestions', []))}")
            for i, sugg in enumerate(result.get('suggestions', [])):
                print(f"  Option {i+1}: {sugg.get('corrected_text', 'N/A')[:60]}")
        else:
            print(f"✗ Error: {grammar_resp.status_code}")
            print(f"Response: {grammar_resp.text}")
            
    except Exception as e:
        print(f"Exception: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_grammar())
