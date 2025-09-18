import re
from services import logging


logger = logging.get_logger("util")

def extract_guardrails_answer(input_string):
    """
    Extract the guardrails answer from the AI model response.
    
    Looks for content within <response></response> tags and returns it.
    
    Args:
        input_string (str): The AI model response containing XML tags
        
    Returns:
        str: The extracted response content (typically "yes" or "no")
        
    Raises:
        ValueError: If no response tags are found or input is invalid
    """
    try:
        if not input_string or not input_string.strip():
            logger.error("❌ Empty or whitespace-only input provided to extract_guardrails_answer")
            raise ValueError("Input string cannot be empty")
        
        # Define regex pattern to capture the contents within <response> tags
        response_pattern = r"<response>(.*?)</response>"
        
        match = re.search(response_pattern, input_string, re.DOTALL | re.IGNORECASE)
        
        if not match:
            logger.error(f"❌ No <response> tags found in input: {input_string[:200]}...")
            raise ValueError("No <response> tags found in the input string")
        
        response_content = match.group(1).strip()
        
        if not response_content:
            logger.error("❌ Empty content found within <response> tags")
            raise ValueError("Empty content found within <response> tags")
        
        logger.debug(f"✅ Successfully extracted response: {response_content}")
        return response_content
        
    except ValueError:
        # Re-raise ValueError as is
        raise
    except Exception as e:
        logger.error(f"❌ Unexpected error in extract_guardrails_answer: {str(e)}")
        raise ValueError(f"Failed to extract guardrails answer: {str(e)}")