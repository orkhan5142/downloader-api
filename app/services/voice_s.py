import whisper
import tempfile
import os
from typing import Dict, Optional

# Load the model once when the service starts
model = whisper.load_model("base")  # Using 'base' model for better accuracy

def transcribe_audio(
    audio_data: bytes,
    language: Optional[str] = None
) -> Dict[str, str]:
    """
    Transcribe audio bytes to text using Whisper (no size limits)
    """
    try:
        # Save audio bytes to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(audio_data)
            tmp_path = tmp.name
        
        # Use Whisper's built-in audio loading which handles any length
        result = model.transcribe(
            tmp_path, 
            language=language,
            fp16=False  # Disable if not using GPU
        )
        
        # Clean up temporary file
        os.unlink(tmp_path)
        
        return {
            "text": result["text"],
            "language": result["language"]
        }
        
    except Exception as e:
        # Clean up temporary file if it exists
        if 'tmp_path' in locals() and os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise e