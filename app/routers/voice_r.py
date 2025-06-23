from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from app.services.voice_s import transcribe_audio
from typing import Optional

router = APIRouter()

@router.post("/transcribe")
async def transcribe_voice(
    file: UploadFile = File(..., description="Audio file to transcribe (any size)"),
    language: Optional[str] = None
):
    """
    Transcribe any audio file to text using Whisper (no size limits)
    
    Parameters:
    - file: Audio file (mp3, wav, etc.)
    - language: Optional language code (e.g., 'en', 'es')
    """
    if not file.content_type.startswith('audio/'):
        raise HTTPException(
            status_code=400, 
            detail="File must be an audio file"
        )

    try:
        contents = await file.read()
        result = transcribe_audio(contents, language)
        
        return JSONResponse(content={
            "status": "success",
            "text": result["text"],
            "language": result["language"]
        })
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Transcription failed: {str(e)}"
        )