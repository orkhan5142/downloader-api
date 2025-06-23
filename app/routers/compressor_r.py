# compressor_r.py
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import Response, HTMLResponse, FileResponse
from typing import Optional
from PIL import Image
import io
import os
from datetime import datetime
import ffmpeg
from pathlib import Path

router = APIRouter()

# Configuration
UPLOAD_FOLDER = "static/uploads"
COMPRESSED_FOLDER = "static/compressed"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(COMPRESSED_FOLDER, exist_ok=True)

@router.get("/", response_class=HTMLResponse)
async def get_compressor():
    return FileResponse("templates/index.html")

@router.get("/video", response_class=HTMLResponse)
async def get_video_compressor():
    return FileResponse("templates/video.html")

@router.post("/compress/image")
async def compress_image(
    file: UploadFile = File(...),
    quality: int = Form(50, ge=1, le=100),
    width: Optional[int] = Form(None),
    height: Optional[int] = Form(None)
):
    """Compress an image with optional resizing"""
    try:
        # Read the image
        contents = await file.read()
        original_size = len(contents)
        img = Image.open(io.BytesIO(contents))
        
        # Convert to RGB if necessary
        if img.mode in ('RGBA', 'LA', 'P'):
            img = img.convert('RGB')
        
        # Resize if dimensions provided
        if width and height:
            img = img.resize((width, height), Image.LANCZOS)
        
        # Prepare output buffer
        output_buffer = io.BytesIO()
        
        # Save with compression
        img.save(output_buffer, 
                format=img.format if img.format else 'JPEG',
                quality=quality,
                optimize=True)
        
        output_buffer.seek(0)
        compressed_data = output_buffer.getvalue()
        
        # Check if compression actually reduced size
        if len(compressed_data) >= original_size:
            # Try with lower quality until we get reduction
            for q in range(quality-5, 0, -5):
                output_buffer = io.BytesIO()
                img.save(output_buffer,
                        format=img.format if img.format else 'JPEG',
                        quality=q,
                        optimize=True)
                output_buffer.seek(0)
                compressed_data = output_buffer.getvalue()
                if len(compressed_data) < original_size:
                    break
        
        # Determine content type
        content_type = f"image/{img.format.lower()}" if img.format else "image/jpeg"
        
        return Response(
            content=compressed_data,
            media_type=content_type,
            headers={"content-length": str(len(compressed_data))}
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image compression failed: {str(e)}")

@router.post("/compress/video")
async def compress_video(
    file: UploadFile = File(...),
    crf: int = Form(28, ge=0, le=51),
    preset: str = Form("medium"),
    resolution: Optional[str] = Form(None)
):
    """Compress a video with optional resizing"""
    try:
        # Create temp file
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        input_filename = f"temp_{timestamp}_{file.filename}"
        input_path = os.path.join(UPLOAD_FOLDER, input_filename)
        
        # Save the uploaded file temporarily
        with open(input_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Prepare output path
        output_filename = f"compressed_{timestamp}_{Path(file.filename).stem}.mp4"
        output_path = os.path.join(COMPRESSED_FOLDER, output_filename)
        
        # Build FFmpeg command
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
        
        # Return the compressed file
        return FileResponse(
            output_path,
            media_type="video/mp4",
            filename=output_filename
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Video compression failed: {str(e)}")
    finally:
        # Clean up temp file
        if os.path.exists(input_path):
            os.remove(input_path)