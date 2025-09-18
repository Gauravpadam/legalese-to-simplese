from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
import tempfile
import os
from pathlib import Path
import shutil
from typing import List
import time

from services.logging import get_logger, log_with_context
from utils.helper import pdf_to_pngs, process_images_to_text

router = APIRouter(prefix="/upload", tags=["Upload"])
logger = get_logger("upload_router")

# Supported file types
SUPPORTED_EXTENSIONS = {".pdf", ".txt"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

async def validate_file(file: UploadFile = File(...)):
    """Validate uploaded file size and type."""
    
    logger.debug(f"Validating file: {file.filename}")
    
    # Check file extension
    file_extension = Path(file.filename).suffix.lower()
    if file_extension not in SUPPORTED_EXTENSIONS:
        logger.error(f"Unsupported file type: {file_extension}")
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Supported types: {', '.join(SUPPORTED_EXTENSIONS)}"
        )
    
    # Reset file pointer to beginning
    await file.seek(0)
    
    # Check file size by reading in chunks
    file_size = 0
    chunk_size = 8192
    
    while True:
        chunk = await file.read(chunk_size)
        if not chunk:
            break
        file_size += len(chunk)
        
        if file_size > MAX_FILE_SIZE:
            logger.error(f"File too large: {file_size} bytes")
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)}MB"
            )
    
    # Reset file pointer back to beginning
    await file.seek(0)
    
    logger.debug(f"File validation passed: {file.filename}, size: {file_size} bytes")
    return file

@router.post("/process-document")
async def process_document(file: UploadFile = Depends(validate_file)):
    """
    Process uploaded document (PDF, TXT) by converting to images and then extracting text using AWS Bedrock.
    
    For PDF files: Converts to PNG images, then uses AWS Bedrock Claude vision model for text extraction.
    For TXT files: Reads text content directly.
    """
    start_time = time.time()
    
    logger.info(f"Starting document processing for: {file.filename}")
    
    # Create temporary directory for processing
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            # Save uploaded file
            temp_file_path = os.path.join(temp_dir, file.filename)
            
            logger.debug(f"Saving file to: {temp_file_path}")
            with open(temp_file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            
            file_extension = Path(file.filename).suffix.lower()
            extracted_text = ""
            image_count = 0
            
            if file_extension == ".pdf":
                extracted_text, image_count = await _process_pdf(temp_file_path, temp_dir)
            elif file_extension == ".txt":
                extracted_text, image_count = await _process_txt(temp_file_path)
            
            duration = time.time() - start_time
            
            log_with_context(
                "upload_router",
                "info",
                "Document processing completed successfully",
                filename=file.filename,
                file_type=file_extension,
                file_size=len(content),
                extracted_text_length=len(extracted_text),
                image_count=image_count,
                duration_seconds=round(duration, 3)
            )
            
            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "filename": file.filename,
                    "file_type": file_extension,
                    "extracted_text": extracted_text,
                    "metadata": {
                        "file_size_bytes": len(content),
                        "text_length": len(extracted_text),
                        "images_generated": image_count,
                        "processing_time_seconds": round(duration, 3)
                    }
                }
            )
            
        except Exception as e:
            duration = time.time() - start_time
            
            log_with_context(
                "upload_router",
                "error",
                f"Document processing failed: {str(e)}",
                filename=file.filename,
                file_type=Path(file.filename).suffix.lower(),
                duration_seconds=round(duration, 3),
                error_type=type(e).__name__
            )
            
            logger.error(f"Error processing document {file.filename}: {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Failed to process document: {str(e)}"
            )

async def _process_pdf(pdf_path: str, temp_dir: str) -> tuple[str, int]:
    """Process PDF file: convert to images, then extract text from images using AWS Bedrock."""
    logger.debug("Processing PDF file using image-to-text workflow")
    
    try:
        # Convert PDF to PNG images
        png_images = pdf_to_pngs(pdf_path)
        image_count = len(png_images)
        
        logger.debug(f"Generated {image_count} PNG images from PDF")
        
        # Process all images to extract text using AWS Bedrock
        logger.info("Converting images to text using AWS Bedrock")
        extracted_text = process_images_to_text(png_images)
        
        logger.debug(f"Extracted {len(extracted_text)} characters from PDF images")
        return extracted_text, image_count
        
    except Exception as e:
        logger.error(f"Error processing PDF: {e}")
        raise

async def _process_txt(txt_path: str) -> tuple[str, int]:
    """Process TXT file: read content directly."""
    logger.debug("Processing TXT file")
    
    try:
        with open(txt_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        logger.debug(f"Read {len(content)} characters from TXT file")
        return content, 0  # No images generated for TXT
        
    except Exception as e:
        logger.error(f"Error processing TXT file: {e}")
        raise

@router.get("/supported-formats")
async def get_supported_formats():
    """Get list of supported file formats."""
    return {
        "supported_formats": list(SUPPORTED_EXTENSIONS),
        "max_file_size_mb": MAX_FILE_SIZE // (1024 * 1024),
        "processing_workflow": {
            "pdf": "PDF → PNG images → AWS Bedrock image-to-text conversion",
            "txt": "Direct text reading"
        }
    }