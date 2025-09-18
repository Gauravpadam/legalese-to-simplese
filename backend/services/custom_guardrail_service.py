"""
Custom Guardrail Service for validating user questions and inputs.

This service uses LLM to check if user questions meet certain criteria
and are not malicious (e.g., containing scripts, harmful content, etc.).
"""

from utils.helper import extract_guardrails_answer
from services.llm_service import ask_question
from services.logging import get_logger, log_with_context
from prompts.guardrail_prompts import guardrails_system_prompt, guardrails_user_prompt
import re
import time
from typing import Optional

logger = get_logger("guardrail_service")


async def validate_user_question(user_input: str) -> bool:
    """
    Validate if a user question meets safety and criteria requirements.
    
    This function uses the LLM to analyze user input and determine if it:
    - Falls under acceptable criteria
    - Doesn't contain malicious content (scripts, harmful requests, etc.)
    - Is appropriate for the legal document simplification context
    
    Args:
        user_input (str): The user's question/input to validate
        system_prompt (str): System message for the guardrail LLM (to be filled later)
        user_prompt (str): User message template for the guardrail LLM (to be filled later)
        
    Returns:
        bool: True if the input is valid and safe, False otherwise
    """
    start_time = time.time()
    
    logger.info("Starting guardrail validation")
    logger.info(f"User input length: {len(user_input)} characters")
    
    try:

        safe = is_question_safe(user_input)
        if not safe:
            logger.warning("Input failed basic safety checks")
            return False
        system_message = guardrails_system_prompt
        user_message = guardrails_user_prompt.replace("{query}", user_input)
        # Placeholder system and user messages - to be customized later
        
        # Create the user message by combining template with actual user input
        # For now, just use the user_input directly if no template provided
        
        logger.info("Calling LLM for guardrail validation")
        
        # Call the LLM to analyze the input
        llm_response = await ask_question(system_message, user_message)
        logger.info(f"LLM response: {llm_response} ")
        
        # Parse the LLM response to determine if input is valid
        # Expecting the LLM to respond with "True" or "False" or similar
        is_valid = extract_guardrails_answer(llm_response)
        logger.info(f"Extracted guardrail answer: {is_valid}")
        
        duration = time.time() - start_time
        
        log_with_context(
            "guardrail_service",
            "info",
            "Guardrail validation completed",
            user_input_length=len(user_input),
            validation_result=is_valid,
            llm_response_length=len(llm_response) if llm_response else 0,
            duration_seconds=round(duration, 3)
        )
        
        return is_valid
        
    except Exception as e:
        duration = time.time() - start_time
        
        log_with_context(
            "guardrail_service",
            "error",
            f"Guardrail validation failed: {str(e)}",
            user_input_length=len(user_input),
            duration_seconds=round(duration, 3),
            error_type=type(e).__name__
        )
        
        logger.error(f"Error in validate_user_question: {e}", exc_info=True)
        
        # In case of error, default to False (reject input) for safety
        logger.warning("Defaulting to INVALID due to error for safety")
        return False


def is_question_safe(question: str) -> bool:
    """
    Synchronous wrapper for basic question safety checks before async guardrail check.
    
    Performs basic validation without AI model calls:
    - Checks for extremely long questions
    - Validates basic format
    - Checks for obvious malicious patterns
    
    Args:
        question (str): The question to validate
        
    Returns:
        bool: True if the question passes basic safety checks, False otherwise
    """
    try:
        if not question or not question.strip():
            return False
        
        # Check question length (prevent extremely long inputs)
        if len(question.strip()) > 10000:
            logger.warning(f"⚠️ Question too long: {len(question)} characters")
            return False
        
        # Check for basic malicious patterns
        malicious_patterns = [
            r"<script",
            r"javascript:",
            r"data:text/html",
            r"<iframe",
            r"eval\s*\(",
        ]
        
        for pattern in malicious_patterns:
            if re.search(pattern, question, re.IGNORECASE):
                logger.warning(f"⚠️ Potentially malicious pattern detected in question")
                return False
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error in basic question safety check: {str(e)}")
        return False