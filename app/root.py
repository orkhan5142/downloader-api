# app/root.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def home():
    return {"message": "YouTube Downloader API is working."}