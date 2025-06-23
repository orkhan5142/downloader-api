# image_service.py
import os
import uuid
from io import BytesIO
from tempfile import NamedTemporaryFile
from fastapi import UploadFile
from PIL import Image
import cairosvg
import pillow_heif
import logging
import cv2
import numpy as np
from svgwrite import Drawing

class ImageConverter:
    
    async def _save_upload_file(self, file: UploadFile, extension: str) -> str:
        """Save uploaded file to temporary location"""
        temp_file = NamedTemporaryFile(delete=False, suffix=f".{extension}")
        await file.seek(0)
        contents = await file.read()
        temp_file.write(contents)
        temp_file.close()
        return temp_file.name

    async def convert_image_fixed(
        self,
        file: UploadFile,
        target_format: str,
    ) -> str:
        """
        Convert image to specified format with fixed default settings
        """
        # Default fixed values
        QUALITY = 85
        WIDTH = None  # Keep original dimensions
        HEIGHT = None
        MAINTAIN_ASPECT = True

        # Determine file extension from content type or filename
        file_ext = file.filename.split('.')[-1].lower() if file.filename else 'jpg'
        if file_ext not in ['jpg', 'jpeg', 'png', 'webp', 'bmp', 'tiff', 'tif', 'heic']:
            file_ext = 'jpg'

        input_path = await self._save_upload_file(file, file_ext)
        output_path = f"temp_{uuid.uuid4()}.{target_format}"

        try:
            # Special handling for HEIC format
            if file_ext in ['heic', 'heif']:
                heif_file = pillow_heif.open_heif(input_path)
                image = Image.frombytes(
                    heif_file.mode,
                    heif_file.size,
                    heif_file.data,
                    "raw",
                )
            else:
                image = Image.open(input_path)

            # Convert to RGB if needed (for JPEG)
            if target_format.lower() in ['jpg', 'jpeg'] and image.mode != 'RGB':
                image = image.convert('RGB')

            # Save in target format with fixed options
            save_kwargs = {}
            if target_format.lower() in ['jpg', 'jpeg']:
                save_kwargs['quality'] = QUALITY
                save_kwargs['optimize'] = True
            elif target_format.lower() == 'webp':
                save_kwargs['quality'] = QUALITY
                save_kwargs['method'] = 6  # Default compression method

            image.save(output_path, **save_kwargs)
            return output_path

        except Exception as e:
            if os.path.exists(output_path):
                os.remove(output_path)
            raise RuntimeError(f"Image conversion failed: {str(e)}")
        finally:
            if os.path.exists(input_path):
                os.remove(input_path)

    async def convert_svg_to_raster_fixed(
        self,
        file: UploadFile,
        target_format: str = 'png'
    ) -> str:
        """Convert SVG to raster image with fixed default settings"""
        DEFAULT_SIZE = 1024  # Default size for SVG conversion

        if target_format not in ['png', 'jpeg']:
            raise ValueError("Only PNG and JPEG output formats are supported for SVG conversion")

        input_path = await self._save_upload_file(file, 'svg')
        output_path = f"temp_{uuid.uuid4()}.{target_format}"

        try:
            # Read SVG content
            with open(input_path, 'rb') as f:
                svg_data = f.read()

            if target_format == 'png':
                cairosvg.svg2png(
                    bytestring=svg_data,
                    write_to=output_path,
                    output_width=DEFAULT_SIZE,
                    output_height=DEFAULT_SIZE
                )
            else:  # JPEG
                # CairoSVG doesn't directly support JPEG, so we convert to PNG first then to JPEG
                temp_png = f"temp_{uuid.uuid4()}.png"
                cairosvg.svg2png(
                    bytestring=svg_data,
                    write_to=temp_png,
                    output_width=DEFAULT_SIZE,
                    output_height=DEFAULT_SIZE
                )
                
                # Convert PNG to JPEG
                with Image.open(temp_png) as img:
                    img.convert('RGB').save(output_path, quality=95)
                
                os.remove(temp_png)

            return output_path

        except Exception as e:
            if os.path.exists(output_path):
                os.remove(output_path)
            raise RuntimeError(f"SVG to {target_format.upper()} conversion failed: {str(e)}")
        finally:
            if os.path.exists(input_path):
                os.remove(input_path)

    