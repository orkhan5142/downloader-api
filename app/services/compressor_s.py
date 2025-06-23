# compressor_s.py
from fastapi import UploadFile
from PIL import Image
import io
import os
from datetime import datetime
import ffmpeg
from pathlib import Path

class CompressionService:
    def __init__(self):
        self.UPLOAD_FOLDER = "static/uploads"
        self.COMPRESSED_FOLDER = "static/compressed"
        os.makedirs(self.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(self.COMPRESSED_FOLDER, exist_ok=True)

    async def compress_image(
        self,
        file: UploadFile,
        quality: int = 80,
        width: int = None,
        height: int = None
    ) -> str:
        """Compress and optionally resize an image"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        output_filename = f"compressed_{timestamp}_{file.filename}"
        output_path = os.path.join(self.COMPRESSED_FOLDER, output_filename)
        
        image_data = await file.read()
        img = Image.open(io.BytesIO(image_data))
        
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        
        if width and height:
            img = img.resize((width, height), Image.LANCZOS)
        
        img.save(output_path, "JPEG", quality=quality, optimize=True)
        return output_path

    async def compress_video(
        self,
        file: UploadFile,
        crf: int = 28,
        preset: str = "medium",
        resolution: str = None
    ) -> str:
        """Compress and optionally resize a video"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        input_filename = f"temp_{timestamp}_{file.filename}"
        input_path = os.path.join(self.UPLOAD_FOLDER, input_filename)
        output_filename = f"compressed_{timestamp}_{Path(file.filename).stem}.mp4"
        output_path = os.path.join(self.COMPRESSED_FOLDER, output_filename)
        
        with open(input_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        try:
            ffmpeg_input = ffmpeg.input(input_path)
            
            if resolution:
                ffmpeg_input = ffmpeg_input.filter('scale', resolution)
            
            ffmpeg_input.output(
                output_path,
                vcodec='libx264',
                crf=crf,
                preset=preset,
                acodec='aac',
                strict='experimental'
            ).overwrite_output().run()
            
            return output_path
        finally:
            if os.path.exists(input_path):
                os.remove(input_path)

# Create a service instance
compression_service = CompressionService()