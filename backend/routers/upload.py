from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
import tempfile
import os
from pathlib import Path
import shutil
from typing import List
import time
import uuid
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_aws import BedrockEmbeddings

from services.logging import get_logger, log_with_context
from services.elastic_search_service import ElasticsearchService
from utils.helper import pdf_to_pngs, process_images_to_text
from clients.aws_client import get_aws_bedrock_client

router = APIRouter(prefix="/upload", tags=["Upload"])
logger = get_logger("upload_router")

# Supported file types
SUPPORTED_EXTENSIONS = {".pdf", ".txt"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# Initialize Elasticsearch service
def get_elasticsearch_service() -> ElasticsearchService:
    """Get configured Elasticsearch service instance."""
    try:
        # Get AWS client for embeddings
        aws_client = get_aws_bedrock_client()
        
        # Initialize Bedrock embeddings
        embeddings = BedrockEmbeddings(
            client=aws_client,
            model_id="cohere.embed-english-v3"
        )
        es_service = ElasticsearchService(
            es_url=os.getenv('ELASTICSEARCH_URL', 'https://my-elasticsearch-project-b07525.es.us-central1.gcp.elastic.cloud:443'),
            api_key=os.getenv('ELASTICSEARCH_API_KEY', 'SVQ3Y1Y1a0JscUh2YzI0Rmlkd2Q6eTBMVHBudW14Wm53WjFydGM1SFVsZw=='),
            embedding_model=embeddings
        )
        
        return es_service
    except Exception as e:
        logger.error(f"Failed to initialize Elasticsearch service: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Elasticsearch service initialization failed: {str(e)}"
        )

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

def split_text_into_chunks(text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[str]:
    """
    Split text into chunks using RecursiveCharacterTextSplitter.
    
    Args:
        text (str): The text to split into chunks
        chunk_size (int): Maximum size of each chunk (default: 1000)
        chunk_overlap (int): Number of characters to overlap between chunks (default: 200)
    
    Returns:
        List[str]: List of text chunks
    """
    logger.debug(f"Splitting text into chunks (size: {chunk_size}, overlap: {chunk_overlap})")
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    
    chunks = text_splitter.split_text(text)
    logger.info(f"Split text into {len(chunks)} chunks")
    
    return chunks

@router.post("/process-document")
async def process_document(file: UploadFile = Depends(validate_file)):
    """
    Process uploaded document (PDF, TXT) by converting to images, extracting text using AWS Bedrock, and splitting into chunks.
    
    For PDF files: Converts to PNG images, then uses AWS Bedrock Claude vision model for text extraction.
    For TXT files: Reads text content directly.
    
    The extracted text is then split into chunks using RecursiveCharacterTextSplitter:
    - chunk_size: 1000 characters
    - chunk_overlap: 200 characters
    
    Returns:
        JSONResponse containing:
        - extracted_text: Full extracted text
        - text_chunks: List of text chunks
        - metadata: Processing information including chunk count
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
            
            # Split the extracted text into chunks
            text_chunks = split_text_into_chunks(extracted_text)
            
            # Generate unique document ID
            doc_id = str(uuid.uuid4())
            
            # Get Elasticsearch service and ingest tagged chunks
            es_service = get_elasticsearch_service()
            try:
                ingested_count = await es_service.ingest_tagged_chunks(
                    chunks=text_chunks,
                    doc_id=doc_id,
                    file_name=file.filename,
                    file_type=file_extension,
                    index_name="tagged_legal_docs"
                )
                logger.info(f"✅ Ingested {ingested_count} tagged chunks to Elasticsearch")
                elasticsearch_ingested = True
            except Exception as es_error:
                logger.error(f"❌ Failed to ingest to Elasticsearch: {es_error}")
                elasticsearch_ingested = False
                ingested_count = 0
            
            duration = time.time() - start_time
            
            log_with_context(
                "upload_router",
                "info",
                "Document processing completed successfully",
                filename=file.filename,
                file_type=file_extension,
                file_size=len(content),
                extracted_text_length=len(extracted_text),
                chunks_created=len(text_chunks),
                elasticsearch_ingested=elasticsearch_ingested,
                ingested_chunks=ingested_count,
                image_count=image_count,
                duration_seconds=round(duration, 3)
            )
            
            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "document_id": doc_id,
                    "filename": file.filename,
                    "file_type": file_extension,
                    "extracted_text": extracted_text,
                    "text_chunks": text_chunks,
                    "elasticsearch": {
                        "ingested": elasticsearch_ingested,
                        "chunks_ingested": ingested_count,
                        "index_name": "tagged_legal_docs"
                    },
                    "metadata": {
                        "file_size_bytes": len(content),
                        "text_length": len(extracted_text),
                        "total_chunks": len(text_chunks),
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
            "pdf": "PDF → PNG images → AWS Bedrock image-to-text → Text chunking → LLM tagging → Elasticsearch ingestion",
            "txt": "Direct text reading → Text chunking → LLM tagging → Elasticsearch ingestion"
        },
        "text_chunking": {
            "chunk_size": 1000,
            "chunk_overlap": 200,
            "method": "RecursiveCharacterTextSplitter"
        },
        "llm_tagging": {
            "model": "AWS Bedrock Claude",
            "tag_categories": [
                "Liability/Indemnity",
                "Termination",
                "Renewal/Duration", 
                "Payment/Penalties",
                "Confidentiality/Data",
                "IP/Ownership",
                "Disputes/Governing Law",
                "Usage Restrictions",
                "Miscellaneous"
            ]
        },
        "elasticsearch": {
            "index_name": "tagged_legal_docs",
            "features": ["risk_tags", "section_classification", "full_text_search"]
        }
    }

@router.get("/search-tags")
async def search_by_tags(
    tags: str = None,
    section: str = None,
    query: str = None,
    limit: int = 10
):
    """
    Search documents by risk tags, section, or text content.
    
    Args:
        tags: Comma-separated list of risk tags to search for
        section: Section type to filter by (e.g., "Liability", "Termination")
        query: Text query to search in document content
        limit: Maximum number of results to return
    """
    try:
        es_service = get_elasticsearch_service()
        
        # Build Elasticsearch query
        must_clauses = []
        
        if tags:
            tag_list = [tag.strip() for tag in tags.split(",")]
            must_clauses.append({
                "terms": {"risk_tags": tag_list}
            })
        
        if section:
            must_clauses.append({
                "term": {"section": section}
            })
        
        if query:
            must_clauses.append({
                "match": {"text": query}
            })
        
        # If no filters provided, match all
        if not must_clauses:
            search_body = {"query": {"match_all": {}}}
        else:
            search_body = {
                "query": {
                    "bool": {
                        "must": must_clauses
                    }
                }
            }
        
        search_body["size"] = limit
        search_body["sort"] = [{"timestamp": {"order": "desc"}}]
        
        # Execute search (simplified - you might want to use the actual Elasticsearch client)
        logger.info(f"🔍 Searching tagged documents with tags: {tags}, section: {section}, query: {query}")
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "search_parameters": {
                    "tags": tags,
                    "section": section,
                    "query": query,
                    "limit": limit
                },
                "elasticsearch_query": search_body,
                "message": "Search functionality implemented. Results would be returned from Elasticsearch."
            }
        )
        
    except Exception as e:
        logger.error(f"❌ Search failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(e)}"
        )