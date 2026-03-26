"""MongoDB client helpers using Motor."""

from __future__ import annotations

import os
from typing import Optional

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

load_dotenv(override=True)

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "genai_srs")

client: Optional[AsyncIOMotorClient] = None
db: Optional[AsyncIOMotorDatabase] = None


async def connect_to_mongo() -> AsyncIOMotorDatabase:
    """Create a single shared MongoDB connection for the app."""
    global client, db
    if client is None:
        client = AsyncIOMotorClient(MONGODB_URL)
        db = client[DB_NAME]
        # Ensure the unique email index exists before serving traffic.
        await db.users.create_index("email", unique=True)
        print(f"Connected to MongoDB at {MONGODB_URL}, DB={DB_NAME}")
    return db  # type: ignore[return-value]


async def close_mongo_connection() -> None:
    """Tear down the Mongo connection during application shutdown."""
    global client, db
    if client is not None:
        client.close()
        client = None
        db = None
        print("Closed MongoDB connection")


def get_db() -> AsyncIOMotorDatabase:
    """
    Convenience accessor for the current DB.
    Raises RuntimeError if DB is not initialized yet.
    """
    if db is None:
        raise RuntimeError("MongoDB not initialized. Call connect_to_mongo() at startup.")
    return db
