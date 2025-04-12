# app/routers/youtube_router.py

from fastapi import APIRouter, UploadFile, File
from app.services.downloader import youtube_service

router = APIRouter()

@router.get("/getall")
async def get_all(uri: str):
    return await youtube_service.get_all_video_info(uri)

@router.get("/daudio")
async def download_audio(abr: str, uri: str):
    return await youtube_service.download_audio(abr, uri)

@router.get("/dvideo")
async def download_video(res: str, uri: str):
    return await youtube_service.download_video(res, uri)



@router.get("/tryagain")
async def try_again():
    return {"error": "Invalid URL. Please try again."}
