import re
from langchain_community.document_loaders import PyMuPDFLoader
from PIL import Image
import io
from services.logging import get_logger

logger = get_logger("util")

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
    


def extract_text_from_pdf(pdf_path, txt_path):
    """
    Extract text from PDF and save as formatted markdown.
    
    Args:
        pdf_path (str): Path to the input PDF file
        txt_path (str): Path where the extracted text will be saved
    """
    logger.info(f"Extracting text from PDF: {pdf_path}")
    
    try:
        loader = PyMuPDFLoader(pdf_path)
        # Open the PDF file
        document = loader.load()

        # Initialize an empty string to store extracted text
        extracted_text = document[0].page_content

        # Write the formatted text to a .txt file
        with open(txt_path, 'w', encoding='utf-8') as txt_file:
            txt_file.write(extracted_text)
        
        logger.info(f"Successfully extracted {len(extracted_text)} characters and saved to {txt_path}")
        
    except Exception as e:
        logger.error(f"Error extracting text from PDF {pdf_path}: {e}")
        raise