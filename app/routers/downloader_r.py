from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from app.services.downloader_s import DownloadService
import os
from urllib.parse import quote

router = APIRouter(prefix="/api/downloader", tags=["downloader"])

class UrlRequest(BaseModel):
    url: str

class DownloadRequest(BaseModel):
    url: str
    download_type: str
    format_id: Optional[str] = None

class FormatInfo(BaseModel):
    format_id: str
    ext: str
    resolution: Optional[str]
    filesize: Any
    format_note: Optional[str] 
    vcodec: str
    acodec: str
    fps: Optional[float] = None
    tbr: Optional[float] = None
    protocol: Optional[str] = None

class FormatResponse(BaseModel):
    success: bool
    message: Optional[str] = None
    title: Optional[str] = None
    duration: Optional[int] = None
    thumbnail: Optional[str] = None
    formats: Optional[List[FormatInfo]] = None

@router.post("/detect-platform", response_model=Dict[str, str])
async def detect_platform(request: UrlRequest):
    platform = DownloadService.detect_platform(request.url)
    return {"platform": platform}

@router.post("/get-formats", response_model=FormatResponse)
async def get_formats(request: UrlRequest):
    success, formats_info = DownloadService.get_available_formats(request.url)
    
    if success:
        return {
            "success": True,
            "formats": formats_info["formats"],
            "title": formats_info.get("title", "Unknown")
        }
    else:
        return {
            "success": False,
            "message": formats_info["message"],
            "formats": []
        }

@router.post("/download")
async def download_media(request: DownloadRequest):
    if request.download_type not in ["video", "video only", "audio"]:
        raise HTTPException(status_code=400, detail="Invalid download type")

    # First verify formats are available
    formats_response = await get_formats(UrlRequest(url=request.url))
    if not formats_response.get("success"):
        raise HTTPException(
            status_code=400,
            detail=formats_response.get("message", "Could not fetch available formats")
        )
    
    # If format_id was specified, verify it exists
    if request.format_id:
        available_formats = formats_response.get("formats", [])
        if not any(f.get("format_id") == request.format_id for f in available_formats):
            raise HTTPException(
                status_code=400,
                detail=f"Format {request.format_id} not available for this video"
            )

    # Prepare download to get filename
    prepare_result = DownloadService.prepare_download(
        url=request.url,
        download_type=request.download_type,
        format_id=request.format_id
    )
    if not prepare_result.get("success"):
        raise HTTPException(
            status_code=400,
            detail=prepare_result.get("message", "Download preparation failed")
        )

    filename = quote(prepare_result['filename'], safe='')

    def file_streamer():
        result = DownloadService.download_media(
            url=request.url,
            download_type=request.download_type,
            format_id=request.format_id
        )
        
        if result.get("success") and os.path.exists(result.get("filepath", "")):
            try:
                with open(result["filepath"], "rb") as file:
                    while chunk := file.read(1024 * 1024):
                        yield chunk
            finally:
                try:
                    os.remove(result["filepath"])
                except:
                    pass
        else:
            raise HTTPException(
                status_code=500,
                detail=result.get("message", "Download failed")
            )

    return StreamingResponse(
        file_streamer(),
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )
@router.post("/prepare-download", response_model=Dict[str, Any])
async def prepare_download(request: DownloadRequest):
    """Endpoint to get filename before actual download"""
    return DownloadService.prepare_download(
        url=request.url,
        download_type=request.download_type,
        format_id=request.format_id
    )