
import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, AsyncMock
from app.main import app
from app.dependencies import get_db, get_current_user
from bson.objectid import ObjectId

client = TestClient(app)

# Mock DB dependency
async def override_get_db():
    mock_db = MagicMock()
    mock_db.srs_documents = AsyncMock()
    return mock_db

app.dependency_overrides[get_db] = override_get_db

# Mock user authentication
async def mock_get_current_user():
    return {"_id": ObjectId("65aa12cd9e451234567890ab"), "email": "test@example.com"}

app.dependency_overrides[get_current_user] = mock_get_current_user

@pytest.mark.asyncio
async def test_export_srs_success():
    # Setup
    srs_id = "65aa12cd9e451234567890cd"
    user_id = "65aa12cd9e451234567890ab"
    
    # Mock DB response
    mock_db = await override_get_db()
    mock_db.srs_documents.find_one.return_value = {
        "_id": ObjectId(srs_id),
        "user_id": ObjectId(user_id),
        "srs_document": "# SRS Document\nLine 1\nLine 2"
    }
    
    # We need to apply the override again because verify_export_srs_success is async
    # but TestClient is synchronous (it handles async endpoints by running them).
    # However, override_get_db returns a Coroutine which dependency injection might handle if configured? 
    # Actually, FastAPI dependency with yield or return value works. 
    # But here we defined override_get_db as async, it returns a mock_db.
    # We need to make sure the app uses this mock.
    
    # Let's refine the mock to be simpler for TestClient
    app.dependency_overrides[get_db] = lambda: mock_db
    
    response = client.get(f"/export/{srs_id}")
    
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.headers["content-disposition"].startswith('attachment; filename="srs_')
    assert response.content.startswith(b"%PDF")

def test_export_srs_not_found():
    # Setup
    srs_id = "65aa12cd9e451234567890cd"
    
    mock_db = MagicMock()
    mock_db.srs_documents = AsyncMock()
    mock_db.srs_documents.find_one.return_value = None
    
    app.dependency_overrides[get_db] = lambda: mock_db
    
    response = client.get(f"/export/{srs_id}")
    
    assert response.status_code == 404

def test_export_srs_invalid_id():
    response = client.get("/export/invalid-id")
    assert response.status_code == 400
