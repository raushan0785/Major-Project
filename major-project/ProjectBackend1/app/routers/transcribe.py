"""Transcribe audio via Whisper service."""

from datetime import datetime
import httpx
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from pydantic import BaseModel, ConfigDict
from bson.objectid import ObjectId

from ..dependencies import get_current_user, get_db

router = APIRouter(prefix="/transcribe", tags=["transcribe"])

WHISPER_SERVICE_URL = "http://127.0.0.1:7860/transcribe/"

class TranscriptionResponse(BaseModel):
    message: str
    transcription_id: str
    text: str

    model_config = ConfigDict(extra="ignore")

@router.post("", response_model=TranscriptionResponse)
@router.post("/", response_model=TranscriptionResponse, include_in_schema=False)
async def transcribe_audio(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Upload an audio file, transcribe it via the Whisper service, and store the result.
    """
    # 1. Forward file to Whisper Service
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            # We must read the file content to send it
            file_content = await file.read()
            files = {"file": (file.filename, file_content, file.content_type)}
            
            response = await client.post(WHISPER_SERVICE_URL, files=files)
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=f"Whisper service returned error: {response.text}"
                )
            
            whisper_data = response.json()
            transcription_text = whisper_data.get("transcription")
            
            if transcription_text is None:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="No transcription received from service"
                )

        except httpx.RequestError as exc:
             raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Could not connect to Whisper service ({type(exc).__name__}): {exc}"
            )
    
    # 2. Store result in MongoDB
    transcription_doc = {
        "user_id": ObjectId(current_user["_id"]), # Ensure we store as ObjectId if schema expects it, or str. Usually ObjectId for refs.
        "filename": file.filename,
        "text": transcription_text,
        "created_at": datetime.utcnow()
    }
    
    result = await db.transcriptions.insert_one(transcription_doc)
    
    # 3. Return Response
    return TranscriptionResponse(
        message="Transcription successful",
        transcription_id=str(result.inserted_id),
        text=transcription_text
    )
