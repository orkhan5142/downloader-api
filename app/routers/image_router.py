# image_router.py
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from app.services.image_service import ImageConverter
import os
import uuid

router = APIRouter(prefix="/api/image-converter", tags=["image-converter"])

converter = ImageConverter()

@router.post("/jpeg-to-png")
async def jpeg_to_png(file: UploadFile = File(...)):
    try:
        output_path = await converter.convert_image_fixed(file, target_format="png")
        return FileResponse(output_path, media_type='image/png', filename="converted.png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/png-to-jpeg")
async def png_to_jpeg(file: UploadFile = File(...)):
    try:
        output_path = await converter.convert_image_fixed(file, target_format="jpeg")
        return FileResponse(output_path, media_type='image/jpeg', filename="converted.jpg")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/webp-to-png")
async def webp_to_png(file: UploadFile = File(...)):
    try:
        output_path = await converter.convert_image_fixed(file, target_format="png")
        return FileResponse(output_path, media_type='image/png', filename="converted.png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/png-to-webp")
async def png_to_webp(file: UploadFile = File(...)):
    try:
        output_path = await converter.convert_image_fixed(file, target_format="webp")
        return FileResponse(output_path, media_type='image/webp', filename="converted.webp")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/bmp-to-png")
async def bmp_to_png(file: UploadFile = File(...)):
    try:
        output_path = await converter.convert_image_fixed(file, target_format="png")
        return FileResponse(output_path, media_type='image/png', filename="converted.png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tiff-to-jpeg")
async def tiff_to_jpeg(file: UploadFile = File(...)):
    try:
        output_path = await converter.convert_image_fixed(file, target_format="jpeg")
        return FileResponse(output_path, media_type='image/jpeg', filename="converted.jpg")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/heic-to-jpeg")
async def heic_to_jpeg(file: UploadFile = File(...)):
    try:
        output_path = await converter.convert_image_fixed(file, target_format="jpeg")
        return FileResponse(output_path, media_type='image/jpeg', filename="converted.jpg")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/svg-to-png")
async def svg_to_png(file: UploadFile = File(...)):
    try:
        output_path = await converter.convert_svg_to_raster_fixed(file, target_format="png")
        return FileResponse(output_path, media_type='image/png', filename="converted.png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Opposite conversions
@router.post("/png-to-jpeg")
async def png_to_jpeg(file: UploadFile = File(...)):
    try:
        output_path = await converter.convert_image_fixed(file, target_format="jpeg")
        return FileResponse(output_path, media_type='image/jpeg', filename="converted.jpg")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/jpeg-to-webp")
async def jpeg_to_webp(file: UploadFile = File(...)):
    try:
        output_path = await converter.convert_image_fixed(file, target_format="webp")
        return FileResponse(output_path, media_type='image/webp', filename="converted.webp")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/webp-to-jpeg")
async def webp_to_jpeg(file: UploadFile = File(...)):
    try:
        output_path = await converter.convert_image_fixed(file, target_format="jpeg")
        return FileResponse(output_path, media_type='image/jpeg', filename="converted.jpg")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/png-to-bmp")
async def png_to_bmp(file: UploadFile = File(...)):
    try:
        output_path = await converter.convert_image_fixed(file, target_format="bmp")
        return FileResponse(output_path, media_type='image/bmp', filename="converted.bmp")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/jpeg-to-tiff")
async def jpeg_to_tiff(file: UploadFile = File(...)):
    try:
        output_path = await converter.convert_image_fixed(file, target_format="tiff")
        return FileResponse(output_path, media_type='image/tiff', filename="converted.tiff")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/jpeg-to-heic")
async def jpeg_to_heic(file: UploadFile = File(...)):
    try:
        output_path = await converter.convert_image_fixed(file, target_format="heic")
        return FileResponse(output_path, media_type='image/heic', filename="converted.heic")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/png-to-svg")
async def png_to_svg(file: UploadFile = File(...)):
    try:
        output_path = await converter.convert_raster_to_svg_fixed(file)
        return FileResponse(output_path, media_type='image/svg+xml', filename="converted.svg")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))