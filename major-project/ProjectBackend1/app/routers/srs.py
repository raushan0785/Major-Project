"""SRS generation routes backed by MongoDB."""

from datetime import datetime
import os
import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, model_validator
from bson.objectid import ObjectId
from typing import Optional

from ..dependencies import get_current_user, get_db

router = APIRouter(prefix="/generate_srs", tags=["srs"])


def _normalize_srs_service_url(base_url: str) -> str:
    base = base_url.rstrip("/")
    if base.endswith("/generate/quick") or base.endswith("/generate"):
        return base
    return f"{base}/api/v1/generate/quick"


SRS_SERVICE_URL = _normalize_srs_service_url(
    os.getenv("SRS_SERVICE_URL", "http://127.0.0.1:8001/api/v1/generate/quick")
)

class SRSRequest(BaseModel):
    input_text: Optional[str] = None
    transcription_id: Optional[str] = None
    template_name: Optional[str] = "agile"

    @model_validator(mode='after')
    def check_input_exists(self):
        if not self.input_text and not self.transcription_id:
            raise ValueError("Must provide either input_text or transcription_id.")
        return self

class SRSResponse(BaseModel):
    message: str
    srs_id: str
    srs_document: str

@router.post("", response_model=SRSResponse)
@router.post("/", response_model=SRSResponse, include_in_schema=False)
async def generate_srs(
    request: SRSRequest,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Generate an SRS document from text or a transcription.
    """
    input_text = ""
    transcription_id = None
    trans_oid = None

    # 1. Resolve Input Text
    if request.transcription_id:
        try:
            trans_oid = ObjectId(request.transcription_id)
        except Exception:
             raise HTTPException(status_code=400, detail="Invalid transcription_id format")

        transcription = await db.transcriptions.find_one({
            "_id": trans_oid
            # "user_id": ObjectId(current_user["_id"])  <-- Commented out for debugging
        })
        
        if not transcription:
             raise HTTPException(status_code=404, detail="Transcription not found or access denied")
        
        input_text = transcription.get("text", "")
        transcription_id = request.transcription_id
    elif request.input_text:
        input_text = request.input_text

    if not input_text:
        raise HTTPException(status_code=400, detail="Input text is empty")

    # 2. Call SRS Service
    # Structure payload for the SRS service (srspipeline-main)
    # Target: POST http://127.0.0.1:9000/api/v1/generate/quick
    payload = {
        "user_requirement": input_text,
        "template_name": request.template_name or "agile"
    }

    async with httpx.AsyncClient(timeout=300.0) as client:
        try:
            # We need to verify the actual endpoint of srs service
            # User said: "ProjectBackend1" and "srspipeline-main"
            # srspipeline-main main.py has: app.include_router(router, prefix="/api/v1")
            # And router is from src.api
            # So likely http://localhost:8001/api/v1/generate
            
            response = await client.post(SRS_SERVICE_URL, json=payload)
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=f"SRS service returned error: {response.text}"
                )
            
            srs_data = response.json()
            
            if not srs_data.get("success"):
                 raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"SRS generation failed: {srs_data.get('error')}"
                )
            
            generated_srs = srs_data.get("srs_document")
            template_used = srs_data.get("template_used")

        except httpx.RequestError as exc:
             raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Could not connect to SRS service ({type(exc).__name__}): {exc}"
            )

    # 3. Store in MongoDB
    srs_doc = {
        "user_id": ObjectId(current_user["_id"]),
        "input_text": input_text,
        "srs_document": generated_srs,
        "template_used": template_used,
        "created_at": datetime.utcnow()
    }
    
    if transcription_id:
        srs_doc["transcription_id"] = ObjectId(transcription_id)

    result = await db.srs_documents.insert_one(srs_doc)

    # 4. Return Response
    return SRSResponse(
        message="SRS generated successfully",
        srs_id=str(result.inserted_id),
        srs_document=generated_srs
    )

@router.get("/list")
async def list_srs(
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    List all SRS documents for the current user.
    """
    cursor = db.srs_documents.find({"user_id": ObjectId(current_user["_id"])}).sort("created_at", -1)
    documents = await cursor.to_list(length=100)
    
    results = []
    for doc in documents:
        results.append({
            "srs_id": str(doc["_id"]),
            "input_text": doc.get("input_text", ""),
            "template_used": doc.get("template_used", "Unknown"),
            "created_at": doc.get("created_at")
        })
        
    return results
