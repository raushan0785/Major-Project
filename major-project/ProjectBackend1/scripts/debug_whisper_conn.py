import httpx
import asyncio

URL = "http://127.0.0.1:7860/transcribe/"

async def main():
    print(f"Testing connection to {URL}")
    async with httpx.AsyncClient() as client:
        try:
            # First try a GET to root to see if service is up (assuming app.py has a GET /)
            # app.py has GET / which returns index.html
            root_url = "http://127.0.0.1:7860/"
            print(f"GET {root_url}")
            resp = await client.get(root_url, timeout=5.0)
            print(f"Root response: {resp.status_code}")
        except Exception as e:
            print(f"GET Root failed: {e.__class__.__name__}: {e}")

        # Now try POST to /transcribe/ with a dummy file
        try:
            print(f"POST {URL} with dummy file")
            files = {'file': ('test.txt', b'dummy content', 'text/plain')}
            resp = await client.post(URL, files=files, timeout=10.0)
            print(f"Transcribe response: {resp.status_code}")
            print(f"Body: {resp.text[:100]}")
        except Exception as e:
            print(f"POST Transcribe failed: {e.__class__.__name__}: {e}")

if __name__ == "__main__":
    asyncio.run(main())
