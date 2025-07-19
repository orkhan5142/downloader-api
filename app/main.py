from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import uvicorn



# Create FastAPI app
app = FastAPI(
    title="MultiTool Suite",
    description="A collection of powerful digital tools.",
    version="2.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files (CSS, JS, Images)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Jinja2 Templates
templates = Jinja2Templates(directory="app/templates")

# --- Page Routes ---

@app.get("/", response_class=HTMLResponse, name="home")
async def get_home_page(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/downloader", response_class=HTMLResponse, name="downloader_page")
async def get_downloader_page(request: Request):
    return templates.TemplateResponse("downloader.html", {"request": request})

@app.get("/imagecompressor", response_class=HTMLResponse, name="imagecompressor_page")
async def get_imagecompressor_page(request: Request):
    return templates.TemplateResponse("imagecompressor.html", {"request": request})

@app.get("/voicetotext", response_class=HTMLResponse, name="voicetotext_page")
async def get_voicetotext_page(request: Request):
    return templates.TemplateResponse("VTT.html", {"request": request})

@app.get("/videocompressor", response_class=HTMLResponse, name="videocompressor_page")
async def get_videocompressor_page(request: Request):
    return templates.TemplateResponse("videocompressor.html", {"request": request})

@app.get("/pdfconverter", response_class=HTMLResponse, name="pdfconverter_page")
async def get_pdfconverter_page(request: Request):
    return templates.TemplateResponse("pdfconverter.html", {"request": request})

@app.get("/pdfconvertertypes", response_class=HTMLResponse, name="pdfconvertertypes_page")
async def get_pdfconvertertypes_page(request: Request):
    return templates.TemplateResponse("pdfconvertertypes.html", {"request": request})

@app.get("/imageconverter", response_class=HTMLResponse, name="imageconverter_page")
async def get_imageconverter_page(request: Request):
    return templates.TemplateResponse("imageconverter.html", {"request": request})

@app.get("/imageconvertertypes", response_class=HTMLResponse, name="imageconvertertypes_page")
async def get_imageconvertertypes_page(request: Request):
    return templates.TemplateResponse("imageconvertertypes.html", {"request": request})


# --- API Routes ---
# Include routers
from app.routers.downloader_r import router as download_router

from app.routers.pdf_router import router as pdf_router
from app.routers.voice_r import router as voice_router  # Add this import
from app.routers.compressor_r import router as compressor_router  # Add this import
from app.routers.image_router import router as image_router  # Add this import

app.include_router(download_router)
app.include_router(pdf_router)
app.include_router(voice_router)
app.include_router(compressor_router)  
app.include_router(image_router)
# ... etc.
# from app.routers.downloader_r import router as download_router
# app.include_router(download_router, prefix="/api/downloader", tags=["Downloader"])


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)