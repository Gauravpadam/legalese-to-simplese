from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from services.qa_service import process_user_question
from services.logging import get_logger, log_with_context
from DTO.DTO import QuestionResponse

router = APIRouter(prefix="/qa", tags=["Question & Answer"])

logger = get_logger("qa_router")

class QuestionRequest(BaseModel):
    question: str = Field(..., description="The question to ask", min_length=1, max_length=2000)
    context: str = Field(default="", description="Optional context for the question", max_length=10000)

@router.post("/ask", 
             response_model=QuestionResponse,
             summary="Ask a question",
             description="Submit a question to get an AI-generated answer. Optionally provide context for better responses.")
async def ask_question_endpoint(request: QuestionRequest):
    """
    Ask a question and get an AI-generated response.
    
    - **question**: Your question (required, 1-2000 characters)
    - **context**: Optional context to improve the answer quality (max 10000 characters)
    """
    try:
        logger.info(f"Received question request: {request.question[:100]}...")
        
        # Prepare system message with default context or user-provided context
        if request.context:
            system_message = f"You are a helpful AI assistant. Use the following context to answer questions accurately and helpfully:\n\nContext: {request.context}\n\nPlease provide clear, accurate, and helpful responses based on this context."
        else:
            system_message = "You are a helpful AI assistant. Please provide clear, accurate, and helpful responses to user questions."
        
        # Get response from LLM service
        answer = await process_user_question(request.question)
        
        log_with_context(
            "qa_router",
            "info",
            "Question answered successfully",
            question_length=len(request.question),
            context_length=len(request.context),
            # answer_length=len(answer) if answer else 0
        )
        
        return answer
        
    except Exception as e:
        logger.error(f"Error processing question: {e}", exc_info=True)
        
        log_with_context(
            "qa_router",
            "error",
            f"Question processing failed: {str(e)}",
            question_length=len(request.question),
            context_length=len(request.context),
            error_type=type(e).__name__
        )
        
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process question: {str(e)}"
        )

@router.get("/health",
           summary="QA Service Health Check",
           description="Check if the QA service is operational")
async def qa_health_check():
    """
    Simple health check for the QA service.
    """
    return {
        "service": "qa",
        "status": "healthy",
        "message": "QA service is operational"
    }
