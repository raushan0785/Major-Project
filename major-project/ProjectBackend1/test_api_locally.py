import asyncio
import httpx
from motor.motor_asyncio import AsyncIOMotorClient
from bson.objectid import ObjectId
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.utils.auth import create_access_token

async def test_api():
    client = AsyncIOMotorClient("mongodb://127.0.0.1:27017")
    db = client["genai_srs"]
    
    srs_id = "69a6dd23913d0c3a70f1af5c"
    
    srs_doc = await db.srs_documents.find_one({"_id": ObjectId(srs_id)})
    if not srs_doc:
        srs_id = "69a6e2976a942c64abca6471"
        srs_doc = await db.srs_documents.find_one({"_id": ObjectId(srs_id)})
        
    print(f"Found SRS document {srs_id}, user_id={srs_doc['user_id']}")
    user_id = str(srs_doc["user_id"])
    
    token = create_access_token({"sub": user_id})
    print(f"Generated token.")
    
    async with httpx.AsyncClient() as http:
        resp = await http.get(
            f"http://127.0.0.1:8000/export/{srs_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        print(f"Status: {resp.status_code}")
        if resp.status_code != 200:
            print("Response:", resp.text)
        else:
            print("Success! Got bytes:", len(resp.content))

if __name__ == "__main__":
    asyncio.run(test_api())
