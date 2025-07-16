# from fastapi import APIRouter, UploadFile, File, HTTPException, Form
# from fastapi.responses import JSONResponse
# from app.services.voice_s import transcribe_audio
# from typing import Optional

# router = APIRouter()

# @router.post("/transcribe")
# async def transcribe_voice(
#     file: UploadFile = File(..., description="Audio file to be transcribed (e.g., mp3, wav, m4a, ogg, webm)."),
#     language: Optional[str] = Form(None, description="Optional: Language of the audio in ISO 639-1 format (e.g., 'en', 'es'). If not provided, the model will detect it.")
# ):
#     """
#     Transcribes an audio file to text using the Whisper model.

#     This endpoint accepts an audio file and returns the transcribed text.
#     It's designed to handle large files by streaming them to a temporary file on the server.

#     - **file**: The audio file to process.
#     - **language**: Optional two-letter language code to guide the transcription.
#     """
#     if not file.content_type or not file.content_type.startswith('audio/'):
#         raise HTTPException(
#             status_code=400,
#             detail=f"Invalid file type: '{file.content_type}'. Please upload a valid audio file."
#         )

#     try:
#         # Read file contents into memory. For very large files, streaming to a temp file
#         # directly might be better, but this is simpler and works for most cases.
#         contents = await file.read()
        
#         # Call the transcription service
#         result = transcribe_audio(contents, language)
        
#         return JSONResponse(content={
#             "status": "success",
#             "text": result["text"],
#             "language": result["language"]
#         })
    
#     except Exception as e:
#         # Log the exception for debugging purposes
#         print(f"An error occurred during transcription: {e}")
#         raise HTTPException(
#             status_code=500,
#             detail=f"An unexpected error occurred during transcription. Please try again later."
#         )