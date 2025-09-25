from services.elastic_search_service import ElasticsearchService
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from langchain.schema import Document
from clients.ollama import OllamaClient
from services.llm_service import ask_question
from utils.helper import extract_text_from_pdf
from fastapi.responses import JSONResponse
import tempfile
import os
from pathlib import Path
from typing import List
import time
import uuid
import json
from langchain.text_splitter import RecursiveCharacterTextSplitter
from services.logging import get_logger, log_with_context
from services.elastic_search_service import ElasticsearchService
from clients.ollama import OllamaClient


# Supported file types
SUPPORTED_EXTENSIONS = {".pdf"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

class UploadService:

    logger = get_logger("UploadService")

    def __init__(self):
        self.elasticSearchService = ElasticsearchService()

    def split_text_into_chunks(self, text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[str]:
        """
        Split text into chunks using RecursiveCharacterTextSplitter.
        
        Args:
            text (str): The text to split into chunks
            chunk_size (int): Maximum size of each chunk (default: 1000)
            chunk_overlap (int): Number of characters to overlap between chunks (default: 200)
        
        Returns:
            List[str]: List of text chunks
        """
        self.logger.debug(f"Splitting text into chunks (size: {chunk_size}, overlap: {chunk_overlap})")
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        chunks = text_splitter.split_text(text)
        self.logger.info(f"Split text into {len(chunks)} chunks")
        
        return chunks

    def analysis_structure(self, Document_Type: str = "Unknown Document", 
                        Main_Purpose: str = "Purpose not determined",
                        Key_Highlights: List[dict] = None,
                        Risk_Assessment: dict = None,
                        Key_Terms: List[dict] = None,
                        Suggested_Questions: List[str] = None) -> dict:
        """
        Create a structured analysis object that matches the expected JSON schema for legal document analysis.
        This function serves as a data validation and normalization tool that enforces consistent structure
        across all document analysis outputs, ensuring compatibility with frontend components and API consumers.
        
        The function validates input data types, provides sensible defaults for missing fields, and transforms
        malformed data into the correct schema format. This is particularly useful when processing LLM responses
        that may have inconsistent formatting or missing fields.
        
        Schema Structure:
        - Document_Type: Classification of the legal document (contracts, agreements, disputes, etc.)
        - Main_Purpose: Executive summary of the document's primary objective
        - Key_Highlights: Critical points that require user attention (terms, clauses, obligations)
        - Risk_Assessment: Comprehensive risk analysis with numerical scoring and categorized risks
        - Key_Terms: Important legal terminology with explanations for non-legal users
        - Suggested_Questions: Contextual questions to help users understand the document better
        
        Args:
            Document_Type (str): Type of document (Property dispute, Rental agreement, Criminal chargesheet, Employment contract, Service agreement, etc.)
            Main_Purpose (str): Main purpose of the document (The primary objective, intent, or goal of the legal document in plain language)
            Key_Highlights (List[dict]): List of important highlights (Critical information formatted as [{"data": "highlight text"}, {"data": "another highlight"}] - focuses on obligations, rights, penalties, deadlines)
            Risk_Assessment (dict): Risk assessment with score and categorized risks (Example: {"Risk_Score": 6, "High_Risk": [{"title": "Late Payment", "description": "5% penalty"}], "Medium_Risk": [], "Low_Risk": []})
            Key_Terms (List[dict]): List of key terms with titles and descriptions (Legal jargon explained in simple terms: [{"title": "Indemnification", "description": "Protection from legal liability"}])
            Suggested_Questions (List[str]): List of suggested questions (Contextual questions users might ask: ["What are my obligations?", "When does this expire?", "How can I terminate this?"])
        
        Returns:
            dict: Properly structured analysis matching the JSON schema with validated data types, 
                ensuring all required fields are present with appropriate defaults and proper formatting
                for consistent API responses and frontend consumption.
        """
        
        # Default values for complex fields
        if Key_Highlights is None:
            Key_Highlights = [{"data": "No highlights identified"}]
        
        if Risk_Assessment is None:
            Risk_Assessment = {
                "Risk_Score": 5,
                "High_Risk": [],
                "Medium_Risk": [],
                "Low_Risk": []
            }
        
        if Key_Terms is None:
            Key_Terms = [{"title": "No terms", "description": "No key terms identified"}]
        
        if Suggested_Questions is None:
            Suggested_Questions = [
                "What are the main obligations?",
                "What are the risks?", 
                "How can this be terminated?"
            ]
        
        # Validate and structure Risk_Assessment
        risk_assessment = {
            "Risk_Score": Risk_Assessment.get("Risk_Score", 5),
            "High_Risk": Risk_Assessment.get("High_Risk", []),
            "Medium_Risk": Risk_Assessment.get("Medium_Risk", []),
            "Low_Risk": Risk_Assessment.get("Low_Risk", [])
        }
        
        # Ensure Risk_Score is an integer between 1-10
        risk_score = risk_assessment["Risk_Score"]
        if not isinstance(risk_score, int) or risk_score < 1 or risk_score > 10:
            risk_assessment["Risk_Score"] = 5
        
        # Validate Key_Highlights structure
        validated_highlights = []
        for highlight in Key_Highlights:
            if isinstance(highlight, dict) and "data" in highlight:
                validated_highlights.append({"data": str(highlight["data"])})
            elif isinstance(highlight, str):
                validated_highlights.append({"data": highlight})
        
        if not validated_highlights:
            validated_highlights = [{"data": "No highlights identified"}]
        
        # Validate Key_Terms structure
        validated_terms = []
        for term in Key_Terms:
            if isinstance(term, dict) and "title" in term and "description" in term:
                validated_terms.append({
                    "title": str(term["title"]),
                    "description": str(term["description"])
                })
        
        if not validated_terms:
            validated_terms = [{"title": "No terms", "description": "No key terms identified"}]
        
        # Validate risk arrays structure
        for risk_level in ["High_Risk", "Medium_Risk", "Low_Risk"]:
            validated_risks = []
            for risk in risk_assessment[risk_level]:
                if isinstance(risk, dict) and "title" in risk and "description" in risk:
                    validated_risks.append({
                        "title": str(risk["title"]),
                        "description": str(risk["description"])
                    })
            risk_assessment[risk_level] = validated_risks
        
        # Ensure Suggested_Questions are strings
        validated_questions = [str(q) for q in Suggested_Questions if q]
        if not validated_questions:
            validated_questions = [
                "What are the main obligations?",
                "What are the risks?",
                "How can this be terminated?"
            ]
        
        return {
            "Document_Type": str(Document_Type),
            "Main_Purpose": str(Main_Purpose),
            "Key_Highlights": validated_highlights,
            "Risk_Assessment": risk_assessment,
            "Key_Terms": validated_terms,
            "Suggested_Questions": validated_questions
        }


    async def validate_file(self, file: File):
        """Validate uploaded file size and type."""
        
        self.logger.debug(f"Validating file: {file.filename}")
        
        # Check file extension
        file_extension = Path(file.filename).suffix.lower()
        if file_extension not in SUPPORTED_EXTENSIONS:
            self.logger.error(f"Unsupported file type: {file_extension}")
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Supported types: {', '.join(SUPPORTED_EXTENSIONS)}"
            )
        
        # Check file size by reading in chunks
        file_size = os.path.getsize(file)
        
        # Shit code (you really think size of the file must only depend on the characters it has?)
        
        # while True:
        #     chunk = await file.read(chunk_size)
        #     if not chunk:
        #         break
        #     file_size += len(chunk)
            
        #     if file_size > MAX_FILE_SIZE:
        #         self.logger.error(f"File too large: {file_size} bytes")
        #         raise HTTPException(
        #             status_code=413,
        #             detail=f"File too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)}MB"
        #         )


        if file_size < MAX_FILE_SIZE:
            self.logger.debug(f"File validation passed: {file}, size: {file_size} bytes")
            return file
        else:
            raise HTTPException(400, "File size exceeded.")

    async def analyze_document_with_llm(self, text: str) -> dict:
        """
        Analyze the entire document text using LLM to generate structured analysis.
        
        Args:
            text (str): The full extracted text from the document
        
        Returns:
            dict: Structured document analysis
        """
        self.logger.debug("Analyzing document with LLM for structured output")
        
        try:
            
            system_prompt = """
                You are a legal document analyzer. Analyze the provided document text and return a structured JSON analysis.

                You are provided a tool called `analysis_structure` to fulfill your purpose.
                You are supposed to call this tool and get the desired response from the tool.

                If you do not call this tool, the output will not be accepted. Calling the tool with a valid parameter set is mandatory.
                """

            human_prompt = f"""Document Text:
                -----
                {text[:8000]}...
                -----

                Analyze this document and return the structured JSON analysis."""
            
            model_instance = OllamaClient.get_client().bind_tools([self.analysis_structure])

            # Call the LLM service
            raw_response = await ask_question(system_prompt, human_prompt, model_instance)
            
            # Parse and validate the response
            try:
                analysis = json.loads(raw_response or "{}")
                
                # Ensure all required fields exist with defaults
                required_structure = {
                    "Document_Type": analysis.get("Document_Type", "Unknown Document"),
                    "Main_Purpose": analysis.get("Main_Purpose", "Purpose not determined"),
                    "Key_Highlights": analysis.get("Key_Highlights", [{"data": "No highlights identified"}]),
                    "Risk_Assessment": {
                        "Risk_Score": analysis.get("Risk_Assessment", {}).get("Risk_Score", 5),
                        "High_Risk": analysis.get("Risk_Assessment", {}).get("High_Risk", []),
                        "Medium_Risk": analysis.get("Risk_Assessment", {}).get("Medium_Risk", []),
                        "Low_Risk": analysis.get("Risk_Assessment", {}).get("Low_Risk", [])
                    },
                    "Key_Terms": analysis.get("Key_Terms", [{"title": "No terms", "description": "No key terms identified"}]),
                    "Suggested_Questions": analysis.get("Suggested_Questions", ["What are the main obligations?", "What are the risks?", "How can this be terminated?"])
                }
                
                self.logger.info(f"✅ LLM document analysis completed successfully")
                return required_structure
                
            except json.JSONDecodeError as e:
                self.logger.error(f"❌ Failed to parse LLM response as JSON: {e}")
                return self._get_default_analysis()
                
        except Exception as e:
            self.logger.error(f"❌ Error analyzing document with LLM: {str(e)}")
            return self._get_default_analysis()
    
    async def process_document(self, file: UploadFile):
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
        
        self.logger.info(f"Starting document processing for: {file.filename}")
        
        # Create temporary directory for processing
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                # Save uploaded file
                temp_file_path = os.path.join(temp_dir, file.filename)
                
                self.logger.debug(f"Saving file to: {temp_file_path}")
                with open(temp_file_path, "wb") as buffer:
                    content = await file.read()
                    buffer.write(content)
                
                file_extension = Path(file.filename).suffix.lower()
                extracted_text = ""
                image_count = 0
                
                if file_extension == ".pdf":
                    extracted_text = await self._process_pdf(temp_file_path, temp_dir)
                elif file_extension == ".txt":
                    extracted_text = await self._process_txt(temp_file_path)
                
                # Split the extracted text into chunks
                text_chunks = self.split_text_into_chunks(extracted_text)

                docs = []
                for text_chunk in text_chunks:
                    doc = Document(text_chunk)
                    docs.append(doc)


                
                # Analyze the full document with LLM
                self.logger.info("🤖 Analyzing document with LLM for structured output")
                document_analysis = await self.analyze_document_with_llm(extracted_text)
                
                # Generate unique document ID
                doc_id = str(uuid.uuid4())
                
                
                try:
                    ingested_count = self.elasticSearchService.ingest_documents(
                        docs,
                        index_name="doc_index"
                    )
                    self.logger.info(f"✅ Ingested {ingested_count} tagged chunks to Elasticsearch")
                    elasticsearch_ingested = True
                except Exception as es_error:
                    self.logger.error(f"❌ Failed to ingest to Elasticsearch: {es_error}")
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
                        "document_analysis": document_analysis,
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
                
                self.logger.error(f"Error processing document {file.filename}: {e}", exc_info=True)
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to process document: {str(e)}"
                )

    def _get_default_analysis() -> dict:
        """Return default analysis structure when LLM analysis fails."""
        return {
            "Document_Type": "Unknown Document",
            "Main_Purpose": "Unable to determine document purpose due to analysis error",
            "Key_Highlights": [
                {"data": "Document analysis failed"},
                {"data": "Please review document manually"}
            ],
            "Risk_Assessment": {
                "Risk_Score": 5,
                "High_Risk": [],
                "Medium_Risk": []
            },
            "Key_Terms": [
                {"title": "Analysis Error", "description": "Unable to extract key terms"}
            ],
            "Suggested_Questions": [
                "What type of document is this?",
                "What are the main terms?",
                "What should I be concerned about?"
            ]
        }

    async def _process_pdf(self, pdf_path: str, temp_dir: str) -> tuple[str, int]:
        """Process PDF file: convert to images, then extract text from images using AWS Bedrock."""
        self.logger.debug("Processing PDF file using image-to-text workflow")
        
        try:
            # Convert PDF to PNG images

            text = extract_text_from_pdf(pdf_path, temp_dir)
            return text
            
        except Exception as e:
            self.logger.error(f"Error processing PDF: {e}")
            raise

    async def _process_txt(self, txt_path: str) -> tuple[str, int]:
        """Process TXT file: read content directly."""
        self.logger.debug("Processing TXT file")
        
        try:
            with open(txt_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            self.logger.debug(f"Read {len(content)} characters from TXT file")
            return content, 0  # No images generated for TXT
            
        except Exception as e:
            self.logger.error(f"Error processing TXT file: {e}")
            raise

# Good to have

# @router.get("/supported-formats")
# async def get_supported_formats():
#     """Get list of supported file formats."""
#     return {
#         "supported_formats": list(SUPPORTED_EXTENSIONS),
#         "max_file_size_mb": MAX_FILE_SIZE // (1024 * 1024),
#         "processing_workflow": {
#             "pdf": "PDF → PNG images → AWS Bedrock image-to-text → Text chunking → LLM tagging → Elasticsearch ingestion",
#             "txt": "Direct text reading → Text chunking → LLM tagging → Elasticsearch ingestion"
#         },
#         "text_chunking": {
#             "chunk_size": 1000,
#             "chunk_overlap": 200,
#             "method": "RecursiveCharacterTextSplitter"
#         },
#         "llm_tagging": {
#             "model": "AWS Bedrock Claude",
#             "tag_categories": [
#                 "Liability/Indemnity",
#                 "Termination",
#                 "Renewal/Duration", 
#                 "Payment/Penalties",
#                 "Confidentiality/Data",
#                 "IP/Ownership",
#                 "Disputes/Governing Law",
#                 "Usage Restrictions",
#                 "Miscellaneous"
#             ]
#         },
#         "elasticsearch": {
#             "index_name": "tagged_legal_docs",
#             "features": ["risk_tags", "section_classification", "full_text_search"]
#         }
#     }