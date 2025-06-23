
# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.staticfiles import StaticFiles
# import uvicorn

# from app.root import router as root_router
# from app.routers.downloader_r import router as download_router

# # Create FastAPI app
# app = FastAPI(
#     title="Media Downloader API",
#     description="API for downloading media from various platforms",
#     version="1.0.0"
# )

# # Add CORS middleware
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # For production, you should specify domains
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# app.mount("/static", StaticFiles(directory="templates"), name="static")
# # Include routers
# app.include_router(root_router)
# app.include_router(download_router)

# if __name__ == "__main__":
#     uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
from fastapi.templating import Jinja2Templates

from app.root import router as root_router
from app.routers.downloader_r import router as download_router

from app.routers.pdf_router import router as pdf_router
from app.routers.voice_r import router as voice_router  # Add this import
from app.routers.compressor_r import router as compressor_router  # Add this import
from app.routers.image_router import router as image_router  # Add this import


# Create FastAPI app
app = FastAPI(
    title="Media Downloader API",
    description="API for downloading media from various platforms",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, you should specify domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Include routers
app.include_router(root_router)
app.include_router(download_router)
app.include_router(pdf_router)
app.include_router(voice_router)
app.include_router(compressor_router)  
app.include_router(image_router)
# Include the compressor router

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
