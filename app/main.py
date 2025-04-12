# app/main.py
from fastapi import FastAPI
from app.routers.downloader import youtube_router

app = FastAPI()

# Include routers
app.include_router(youtube_router.router)