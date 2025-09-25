# The upload controller

from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel, Field
from services.llm_service import ask_question
from services.logging import get_logger, log_with_context

from services.UploadService import UploadService

router = APIRouter(tags=["Upload handling API"], prefix="/documents")
logger = get_logger("upload_router")
uploadService = UploadService()



@router.post("/upload", summary="Upload your document", description="Endpoint to upload a file.")
async def upload_document(document: UploadFile = File(...)):
    response = await uploadService.process_document(document)
    return response

