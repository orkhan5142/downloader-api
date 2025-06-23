from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from app.services.pdf_service import PDFConverter
import os
import uuid
from pydantic import BaseModel
from typing import Optional

class HtmlToPdfRequest(BaseModel):
    url: Optional[str] = None

router = APIRouter(prefix="/api/converter", tags=["converter"])

converter = PDFConverter()

@router.post("/jpg-to-pdf")
async def jpg_to_pdf(files: list[UploadFile] = File(...)):
    try:
        output_path = await converter.images_to_pdf(files)
        return FileResponse(output_path, media_type='application/pdf', filename="converted.pdf")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    # finally:
    #     if os.path.exists(output_path):
    #         os.remove(output_path)

@router.post("/word-to-pdf")
async def word_to_pdf(file: UploadFile = File(...)):
    try:
        output_path = await converter.word_to_pdf(file)
        return FileResponse(output_path, media_type='application/pdf', filename="converted.pdf")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    # finally:
    #     if os.path.exists(output_path):
    #         os.remove(output_path)

@router.post("/powerpoint-to-pdf")
async def convert_powerpoint_to_pdf(file: UploadFile = File(...)):
    try:
        output_path = await converter.powerpoint_to_pdf(file)
        return FileResponse(
            output_path,
            media_type='application/pdf',
            filename="converted.pdf",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/excel-to-pdf")
async def excel_to_pdf(file: UploadFile = File(...)):
    try:
        output_path = await converter.excel_to_pdf(file)
        return FileResponse(output_path, media_type='application/pdf', filename="converted.pdf")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/html-to-pdf")
async def html_to_pdf_endpoint(request: HtmlToPdfRequest):
    output_path = None
    try:
        if request.url:
            output_path = await converter.html_to_pdf(request.url, is_url=True)
        else:
            raise HTTPException(status_code=400, detail="Either 'html_content' or 'url' must be provided")
        
        return FileResponse(
            output_path,
            media_type='application/pdf',
            filename="converted.pdf"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


import logging

@router.post("/pdf-to-jpg")
async def pdf_to_jpg(file: UploadFile = File(...), dpi: int = 300):
    try:
        output_path = await converter.pdf_to_jpg(file, dpi)
        return FileResponse(output_path, media_type='application/zip', filename="converted_images.zip")
    except Exception as e:
        logging.error(f"Error during PDF to JPG conversion: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/pdf-to-word")
async def pdf_to_word(file: UploadFile = File(...)):
    try:
        output_path = await converter.pdf_to_word(file)
        return FileResponse(output_path, media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document', filename="converted.docx")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    # finally:
    #     if os.path.exists(output_path):
    #         os.remove(output_path)

@router.post("/pdf-to-powerpoint", response_class=FileResponse)
async def convert_pdf_to_pptx(file: UploadFile = File(...)):
    try:
        output_path = await converter.pdf_to_powerpoint(file)

        return FileResponse(
            output_path,
            media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            filename="converted.pptx"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conversion error: {str(e)}")


@router.post("/pdf-to-excel")
async def pdf_to_excel(file: UploadFile = File(...)):
    try:
        output_path = await converter.pdf_to_excel(file)
        return FileResponse(
            output_path,
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            filename="converted.xlsx",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
