import httpx
import random
import string

def trigger_error():
    random_str = ''.join(random.choices(string.ascii_lowercase, k=5))
    email = f"debug_user_{random_str}@example.com"
    
    url = "http://127.0.0.1:8000/auth/signup"
    payload = {
        "email": email,
        "password": "password123",
        "full_name": "Debug User"
    }
    print(f"Attempting signup with {email}...")
    try:
        response = httpx.post(url, json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.text}")
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    trigger_error()
