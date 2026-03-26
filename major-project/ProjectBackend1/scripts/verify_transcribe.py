import httpx
import asyncio
import wave
import os

BASE_URL = "http://127.0.0.1:8000"
EMAIL = "test_transcribe@example.com"
PASSWORD = "password123"

async def create_dummy_wav(filename="test_audio.wav"):
    with wave.open(filename, "w") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(16000)
        f.writeframes(b"\0" * 16000) # 1 second of silence
    return filename

async def main():
    async with httpx.AsyncClient() as client:
        # 1. Signup
        print(f"Signing up {EMAIL}...")
        resp = await client.post(f"{BASE_URL}/auth/signup", json={
            "email": EMAIL,
            "password": PASSWORD,
            "full_name": "Test User"
        })
        if resp.status_code == 200 or resp.status_code == 201:
            print("Signup successful")
        elif resp.status_code == 400 and "already registered" in resp.text:
            print("User already exists, proceeding...")
        else:
            print(f"Signup failed: {resp.text}")
            return

        # 2. Login
        print("Logging in...")
        resp = await client.post(f"{BASE_URL}/auth/login", json={
            "email": EMAIL,
            "password": PASSWORD
        })
        if resp.status_code != 200:
            print(f"Login failed: {resp.text}")
            return
        
        token = resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("Login successful, got token.")

        # 3. Create dummy audio
        filename = await create_dummy_wav()
        
        # 4. Transcribe
        print("Uploading audio to /transcribe/...")
        with open(filename, "rb") as f:
            files = {"file": (filename, f, "audio/wav")}
            resp = await client.post(f"{BASE_URL}/transcribe/", headers=headers, files=files, timeout=30.0)
        
        if resp.status_code == 200:
            print("Transcription successful!")
            print(resp.json())
        else:
            print(f"Transcription failed: {resp.status_code} {resp.text}")

        # Cleanup
        os.remove(filename)

if __name__ == "__main__":
    asyncio.run(main())
