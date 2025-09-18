import re
import os
import fitz  # PyMuPDF
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
    

import os
import fitz  # PyMuPDF
import re


def format_as_markdown(text):
    """Format text as Markdown with table detection."""
    # This function will format text as Markdown
    # A simple implementation to convert certain patterns to Markdown tables

    # Splitting the text into lines
    lines = text.splitlines()
    markdown_lines = []
    table_started = False

    for line in lines:
        # Check if the line looks like a table header or has consistent separators
        if re.match(r'^\s*\S+\s+\S+', line) and not table_started:
            # Start of a table
            table_started = True
            markdown_lines.append("| " + " | ".join(line.split()) + " |")
            markdown_lines.append("|" + " --- |" * len(line.split()))  # Adding table header separator
        elif table_started and line.strip() == "":
            # End of the table
            table_started = False
            markdown_lines.append("")  # Add a blank line after the table
        elif table_started:
            # Continue table formatting
            markdown_lines.append("| " + " | ".join(line.split()) + " |")
        else:
            # Regular text
            markdown_lines.append(line)

    return "\n".join(markdown_lines)


def extract_text_from_pdf(pdf_path, txt_path):
    """
    Extract text from PDF and save as formatted markdown.
    
    Args:
        pdf_path (str): Path to the input PDF file
        txt_path (str): Path where the extracted text will be saved
    """
    logger.info(f"Extracting text from PDF: {pdf_path}")
    
    try:
        # Open the PDF file
        document = fitz.open(pdf_path)

        # Initialize an empty string to store extracted text
        extracted_text = ""

        # Iterate through each page and extract text
        for page_num in range(len(document)):
            page = document[page_num]
            page_text = page.get_text()
            extracted_text += page_text
            logger.debug(f"Extracted text from page {page_num + 1}: {len(page_text)} characters")

        # Close the document
        document.close()

        # Format the extracted text as Markdown
        markdown_text = format_as_markdown(extracted_text)

        # Write the formatted text to a .txt file
        with open(txt_path, 'w', encoding='utf-8') as txt_file:
            txt_file.write(markdown_text)
        
        logger.info(f"Successfully extracted {len(extracted_text)} characters and saved to {txt_path}")
        
    except Exception as e:
        logger.error(f"Error extracting text from PDF {pdf_path}: {e}")
        raise


def convert_image_to_text(image_bytes):
    """
    Convert image bytes to text using AWS Bedrock Claude model.
    
    Args:
        image_bytes (bytes): The image data as bytes
        
    Returns:
        str: Transcribed text from the image
    """
    import base64
    import json
    from clients.aws_client import get_aws_bedrock_client
    
    logger.info("Converting image to text using AWS Bedrock")
    
    try:
        # Use the existing AWS client from aws_client.py
        runtime = get_aws_bedrock_client()
        
        # Encode image to base64
        encoded_image = base64.b64encode(image_bytes).decode("utf-8")

        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1000,
            "messages": [{
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",  # Changed to PNG since we're using PNG images
                            "data": encoded_image,
                        },
                    },
                    {
                        "type": "text",
                        "text": '''Transcribe the text content from an image page and output in Markdown syntax (not code blocks). Follow these steps:

1. Examine the provided page carefully.

2. Identify all elements present in the page, including headers, body text, footnotes, tables, visualizations, captions, and page numbers, etc.

3. Use markdown syntax to format your output:
    - Headings: # for main, ## for sections, ### for subsections, etc.
    - Lists: * or - for bulleted, 1. 2. 3. for numbered
    - Do not repeat yourself

4. If the element is a visualization
    - Provide a detailed description in natural language
    - Do not transcribe text in the visualization after providing the description

5. If the element is a table
    - Create a markdown table, ensuring every row has the same number of columns
    - Maintain cell alignment as closely as possible
    - Do not split a table into multiple tables
    - If a merged cell spans multiple rows or columns, place the text in the top-left cell and output ' ' for other
    - Use | for column separators, |-|-| for header row separators
    - If a cell has multiple items, list them in separate rows
    - If the table contains sub-headers, separate the sub-headers from the headers in another row

6. If the element is a paragraph
    - Transcribe each text element precisely as it appears

7. If the element is a header, footer, footnote, page number
    - Transcribe each text element precisely as it appears

Here is the image.'''
                    },
                ],
            }],
        })

        # Invoke the model
        response = runtime.invoke_model(
            modelId="anthropic.claude-3-5-sonnet-20240620-v1:0",
            body=body
        )

        # Read the response
        response_body = json.loads(response.get("body").read())

        # Extract the transcription
        transcription = response_body['content'][0]['text']
        
        logger.debug(f"Successfully converted image to text: {len(transcription)} characters")
        return transcription
        
    except Exception as e:
        logger.error(f"Error converting image to text: {e}")
        raise


def process_images_to_text(image_bytes_list):
    """
    Process multiple images and convert them to text.
    
    Args:
        image_bytes_list (list): List of image bytes
        
    Returns:
        str: Combined text from all images
    """
    logger.info(f"Processing {len(image_bytes_list)} images to text")
    
    all_text = []
    
    for i, image_bytes in enumerate(image_bytes_list):
        logger.debug(f"Processing image {i + 1}/{len(image_bytes_list)}")
        
        try:
            text = convert_image_to_text(image_bytes)
            all_text.append(f"## Page {i + 1}\n{text}")
            
        except Exception as e:
            logger.error(f"Error processing image {i + 1}: {e}")
            all_text.append(f"## Page {i + 1}\n[Error processing image: {str(e)}]")
    
    combined_text = "\n\n".join(all_text)
    logger.info(f"Successfully processed all images, total text length: {len(combined_text)} characters")
    
    return combined_text



def pdf_to_pngs(pdf_path, quality=75, max_size=(1024, 1024)):
    """
    Converts a PDF file to a list of PNG images.

    Args:
        pdf_path (str): The path to the local PDF file.
        quality (int, optional): The quality of the output PNG images (default is 75).
        max_size (tuple, optional): The maximum size of the output images (default is (1024, 1024)).

    Returns:
        list: A list of PNG images as bytes.
    """
    logger.info(f"Converting PDF to PNG images: {pdf_path}")
    
    try:
        # Open the PDF file from the local path
        doc = fitz.open(pdf_path)

        pdf_to_png_images = []

        # Iterate through each page of the PDF
        for page_num in range(doc.page_count):
            logger.debug(f"Processing page {page_num + 1}/{doc.page_count}")
            
            # Load the page
            page = doc.load_page(page_num)

            # Render the page as a PNG image with higher DPI for better quality
            pix = page.get_pixmap(matrix=fitz.Matrix(300 / 72, 300 / 72))

            # Save the PNG image to an in-memory file
            image_data = io.BytesIO()
            image_data.write(pix.tobytes("png"))  # Use tobytes to get PNG data
            image_data.seek(0)

            # Open the image with PIL
            image = Image.open(image_data)

            # Resize the image if it exceeds the maximum size
            if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
                original_size = image.size
                image.thumbnail(max_size, Image.Resampling.LANCZOS)
                logger.debug(f"Resized image from {original_size} to {image.size}")

            # Convert the PIL image to bytes
            image_output = io.BytesIO()
            image.save(image_output, format='PNG', optimize=True, quality=quality)
            image_output.seek(0)
            pdf_to_png_image = image_output.getvalue()

            # Append the PNG image bytes to the list
            pdf_to_png_images.append(pdf_to_png_image)

            logger.debug(f"Page {page_num + 1} converted to PNG ({len(pdf_to_png_image)} bytes)")

        # Close the PDF document
        doc.close()
        
        logger.info(f"Successfully converted {len(pdf_to_png_images)} pages to PNG images")
        return pdf_to_png_images
        
    except Exception as e:
        logger.error(f"Error converting PDF to PNG images: {e}")
        raise
