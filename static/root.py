# app/root.py
from fastapi import APIRouter
from fastapi.responses import FileResponse

router = APIRouter()



@router.get("/")
async def home():
    return FileResponse("app/home.html")

@router.get("/home.html")
async def home_page():
    return FileResponse("app/home.html")
    
@router.get("/downloader")
async def downloader_page():
    return FileResponse("app/downloader.html")

@router.get("/imagecompressor")
async def imagecompressor_page():
    return FileResponse("app/imagecompressor.html") 

@router.get("/voicetotext")
async def voicetotext_page():
    return FileResponse("app/VTT.html")

@router.get("/videocompressor")
async def videocompressor_page():
    return FileResponse("app/videocompressor.html")

@router.get("/pdfconverter")
async def pdfconverter_page():
    return FileResponse("app/pdfconverter.html")

@router.get("/pdfconvertertypes")
async def pdfconvertertypes_page():
    return FileResponse("app/pdfconvertertypes.html")

@router.get("/imageconverter")
async def imageconverter_page():
    return FileResponse("app/imageconverter.html")

@router.get("/imageconvertertypes")
async def imageconvertertypes_page():
    return FileResponse("app/imageconvertertypes.html")