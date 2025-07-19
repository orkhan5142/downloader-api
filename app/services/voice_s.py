import whisper
import tempfile
import os
from typing import Dict, Optional

# Load the model once when the service starts to avoid reloading it on every request.
# 'base' model is a good balance of speed and accuracy. For higher accuracy,
# consider 'small' or 'medium', but they require more resources.
try:
    print("Loading Whisper model...")
    model = whisper.load_model("base")
    print("Whisper model loaded successfully.")
except Exception as e:
    print(f"Error loading Whisper model: {e}")
    # Depending on the application's needs, you might want to exit or handle this differently.
    model = None


def transcribe_audio(
    audio_data: bytes,
    language: Optional[str] = None
) -> Dict[str, str]:
    """
    Transcribes audio bytes to text using the pre-loaded Whisper model.

    Args:
        audio_data: The raw bytes of the audio file.
        language: The optional language code (e.g., 'en') for transcription.

    Returns:
        A dictionary containing the transcribed 'text' and detected 'language'.
    
    Raises:
        Exception: If the model is not loaded or if transcription fails.
    """
    if not model:
        raise RuntimeError("Whisper model is not loaded. The service cannot transcribe audio.")

    tmp_path = None
    try:
        # Create a temporary file to store the audio data. Whisper's `transcribe`
        # method works most reliably with file paths.
        with tempfile.NamedTemporaryFile(delete=False, suffix=".tmp") as tmp:
            tmp.write(audio_data)
            tmp_path = tmp.name
        
        # Perform the transcription
        # fp16=False is crucial for CPU-only execution. Set to True if you have a compatible GPU.
        result = model.transcribe(
            tmp_path, 
            language=language,
            fp16=False
        )
        
        return {
            "text": result.get("text", "").strip(),
            "language": result.get("language", "unknown")
        }
        
    except Exception as e:
        # Re-raise the exception to be handled by the API router
        raise e
        
    finally:
        # Ensure the temporary file is always deleted, even if an error occurs.
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)