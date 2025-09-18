import logging
import json
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from langchain_elasticsearch import ElasticsearchStore
from langchain_aws import BedrockEmbeddings
from langchain.schema import Document
from fastapi import HTTPException
from elasticsearch import Elasticsearch, helpers

# Setup logger for this module
logger = logging.getLogger("elasticsearch_service")

# -------------------------------------------------------------------
# CONTROLLED TAG VOCAB
# -------------------------------------------------------------------
TAG_VOCAB: List[Tuple[str, str]] = [
    # Liability / Indemnity
    ("liability_unlimited", "Unlimited liability or no cap"),
    ("indemnity_broad", "Indemnify/defend/hold harmless (one-sided or broad)"),
    ("exclude_conseq_damages", "Excludes consequential/indirect damages"),
    # Termination
    ("termination_convenience", "Termination for convenience / without cause"),
    ("termination_immediate", "Immediate termination rights"),
    ("termination_without_cause", "Termination without cause"),
    # Renewal / Duration
    ("auto_renewal", "Auto-renewal or evergreen term"),
    ("perpetual_term", "Perpetual term"),
    ("minimum_term", "Minimum locked-in term"),
    # Payment / Penalties
    ("holdover_double_rent", "Holdover damages 2x monthly rent"),
    ("late_payment_penalty", "Late fees/penalties"),
    ("interest_free_deposit", "Interest-free security deposit"),
    # Confidentiality / Data
    ("confidentiality_perpetual", "Perpetual confidentiality"),
    ("data_sharing_third_parties", "Broad third-party data sharing"),
    ("breach_notice_hours", "Breach notice within X hours (24/48/72)"),
    # IP / Ownership
    ("ip_assignment", "Assignment of IP / all rights"),
    ("royalty_free_license", "Royalty-free perpetual license"),
    # Disputes / Governing Law
    ("mandatory_arbitration", "Binding/mandatory arbitration"),
    ("exclusive_jurisdiction", "Exclusive jurisdiction"),
    ("governing_law_clause", "Governing law clause"),
    # Usage restrictions (rental)
    ("no_subletting", "No subletting"),
    ("use_restriction_residential", "Residential use only"),
    # Misc
    ("notwithstanding_clause", "Contains 'notwithstanding'"),
    ("best_efforts_clause", "Contains 'best_efforts'"),
    ("sole_discretion", "At its sole discretion"),
]
ALLOWED_TAGS = [slug for slug, _ in TAG_VOCAB]

class ElasticsearchService:
    """
    Service class to handle Elasticsearch operations including document ingestion and retrieval.
    """
    
    def __init__(self, embedding_model: BedrockEmbeddings, es_url: str = "http://localhost:9200", api_key: str = None):
        """
        Initialize the Elasticsearch service.
        
        Args:
            embedding_model: The embedding model to use for vectorization
            es_url: Elasticsearch URL (default: http://localhost:9200)
            api_key: API key for Elasticsearch authentication
        """
        self.embedding_model = embedding_model
        self.es_url = es_url
        self.api_key = api_key
        logger.info(f"🔧 Initialized ElasticsearchService with URL: {es_url}")
    
    def create_vector_store(self, index_name: str) -> ElasticsearchStore:
        """
        Create and return an Elasticsearch vector store instance.
        
        Args:
            index_name: Name of the Elasticsearch index
            
        Returns:
            ElasticsearchStore: Configured vector store instance
            
        Raises:
            HTTPException: If connection to Elasticsearch fails
        """
        try:
            logger.debug(f"🔌 Creating vector store for index: {index_name}")
            
            # Prepare connection parameters
            connection_params = {
                "es_url": self.es_url,
                "index_name": index_name,
                "embedding": self.embedding_model
            }
            
            # Add API key authentication if provided
            if self.api_key:
                connection_params["es_api_key"] = self.api_key
            
            vector_store = ElasticsearchStore(**connection_params)
            logger.info(f"✅ Vector store created successfully for index: {index_name}")
            return vector_store
        except Exception as es_error:
            logger.error(f"❌ Failed to create vector store: {str(es_error)}")
            raise HTTPException(
                status_code=503, 
                detail=f"ElasticSearch connection failed: {str(es_error)}"
            )
    
    def ingest_documents(self, documents: List[Document], index_name: str = "workplace_index") -> Dict[str, Any]:
        """
        Ingest documents into Elasticsearch.
        
        Args:
            documents: List of LangChain Document objects to ingest
            index_name: Name of the Elasticsearch index (default: workplace_index)
            
        Returns:
            Dict containing ingestion results
            
        Raises:
            HTTPException: If document ingestion fails
        """
        try:
            logger.debug(f"💾 Starting document ingestion to index: {index_name}")
            logger.info(f"📊 Ingesting {len(documents)} documents")
            
            # Create vector store
            vector_store = self.create_vector_store(index_name)
            
            # Store documents in Elasticsearch
            vector_store.from_documents(
                documents,
                es_url=self.es_url,
                index_name=index_name,
                embedding=self.embedding_model
            )
            
            logger.info(f"✅ Successfully ingested {len(documents)} documents to index: {index_name}")
            
            return {
                "success": True,
                "documents_ingested": len(documents),
                "index_name": index_name,
                "message": f"Successfully ingested {len(documents)} documents"
            }
            
        except Exception as store_error:
            logger.error(f"❌ Failed to ingest documents: {str(store_error)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to store documents in ElasticSearch: {str(store_error)}"
            )
    
    def get_retriever(self, index_name: str = "workplace_index", search_kwargs: Optional[Dict] = None):
        """
        Get a retriever for querying documents from Elasticsearch.
        
        Args:
            index_name: Name of the Elasticsearch index (default: workplace_index)
            search_kwargs: Additional search parameters for the retriever
            
        Returns:
            Retriever instance for document retrieval
            
        Raises:
            HTTPException: If retriever creation fails
        """
        try:
            logger.debug(f"🔍 Creating retriever for index: {index_name}")
            
            # Create vector store
            vector_store = self.create_vector_store(index_name)
            
            # Create retriever with optional search parameters
            if search_kwargs:
                retriever = vector_store.as_retriever(search_kwargs=search_kwargs)
                logger.debug(f"🔧 Retriever created with custom search kwargs: {search_kwargs}")
            else:
                retriever = vector_store.as_retriever()
                logger.debug("🔧 Retriever created with default settings")
            
            logger.info(f"✅ Retriever created successfully for index: {index_name}")
            return retriever
            
        except Exception as retriever_error:
            logger.error(f"❌ Failed to create retriever: {str(retriever_error)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to create document retriever: {str(retriever_error)}"
            )
    
    def search_documents(self, query: str, index_name: str = "workplace_index", k: int = 4) -> List[Document]:
        """
        Search for relevant documents in Elasticsearch.
        
        Args:
            query: Search query string
            index_name: Name of the Elasticsearch index (default: workplace_index)
            k: Number of documents to retrieve (default: 4)
            
        Returns:
            List of relevant Document objects
            
        Raises:
            HTTPException: If search fails
        """
        try:
            logger.debug(f"🔍 Searching for documents with query: '{query}' in index: {index_name}")
            
            # Create vector store
            vector_store = self.create_vector_store(index_name)
            
            # Perform similarity search
            documents = vector_store.similarity_search(query, k=k)
            
            logger.info(f"✅ Found {len(documents)} relevant documents for query: '{query}'")
            
            return documents
            
        except Exception as search_error:
            logger.error(f"❌ Failed to search documents: {str(search_error)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to search documents: {str(search_error)}"
            )
    
    def get_index_info(self, index_name: str = "workplace_index") -> Dict[str, Any]:
        """
        Get information about an Elasticsearch index.
        
        Args:
            index_name: Name of the Elasticsearch index (default: workplace_index)
            
        Returns:
            Dict containing index information
        """
        try:
            logger.debug(f"📊 Getting info for index: {index_name}")
            
            # Create vector store to access Elasticsearch client
            vector_store = self.create_vector_store(index_name)
            
            # This is a simplified version - you might want to expand this
            # to get actual index statistics from the Elasticsearch client
            info = {
                "index_name": index_name,
                "es_url": self.es_url,
                "status": "connected"
            }
            
            logger.info(f"✅ Retrieved info for index: {index_name}")
            return info
            
        except Exception as info_error:
            logger.error(f"❌ Failed to get index info: {str(info_error)}")
            return {
                "index_name": index_name,
                "es_url": self.es_url,
                "status": "error",
                "error": str(info_error)
            }
    
    def _get_llm_system_prompt(self) -> str:
        """Get the system prompt for LLM tagging."""
        return f"""
You are a contracts clause tagger.

Return STRICT JSON with keys:
- "risk_tags": array of tag slugs chosen ONLY from this allowed list:
{json.dumps(ALLOWED_TAGS)}
- "explanation": <=30 words plain text describing why these tags were chosen
- "section_guess": one or two words indicating clause type (e.g., "Liability","Termination","Payment","Data","IP","Jurisdiction","Usage","Misc")

Rules:
- Output JSON ONLY (no extra text or markdown).
- If unsure, return "risk_tags": [] and a short neutral explanation.
"""

    def _build_human_prompt(self, clause_text: str) -> str:
        """Build the human prompt for LLM tagging."""
        return f"""Clause:
-----
{clause_text}
-----

Return JSON ONLY with keys: risk_tags, explanation, section_guess."""

    def _safe_json_parse(self, llm_response: str) -> Dict:
        """Parse LLM response and enforce allowed tag set; never raise."""
        try:
            data = json.loads(llm_response)
            if not isinstance(data, dict):
                raise ValueError("Expected JSON object")
            data.setdefault("risk_tags", [])
            data.setdefault("explanation", "")
            data.setdefault("section_guess", "Misc")

            # Clean fields
            if not isinstance(data["risk_tags"], list):
                data["risk_tags"] = []
            data["risk_tags"] = [t for t in data["risk_tags"] if t in ALLOWED_TAGS]
            if not isinstance(data["explanation"], str):
                data["explanation"] = ""
            if not isinstance(data["section_guess"], str):
                data["section_guess"] = "Misc"
            return data
        except Exception:
            return {"risk_tags": [], "explanation": "", "section_guess": "Misc"}

    async def tag_chunk_with_llm(self, chunk_text: str) -> Dict[str, Any]:
        """
        Use LLM to tag a text chunk with risk tags.
        
        Args:
            chunk_text: The text chunk to analyze
            
        Returns:
            Dict containing risk_tags, explanation, and section_guess
        """
        try:
            # Import here to avoid circular imports
            from services.custom_guardrail_service import ask_question
            
            system_prompt = self._get_llm_system_prompt()
            human_prompt = self._build_human_prompt(chunk_text)
            
            logger.debug(f"🤖 Analyzing chunk with LLM (length: {len(chunk_text)} chars)")
            
            # Call the LLM service
            raw_response = await ask_question(system_prompt, human_prompt)
            
            # Parse and validate the response
            parsed_response = self._safe_json_parse(raw_response or "")
            
            logger.debug(f"✅ LLM tagged chunk with {len(parsed_response.get('risk_tags', []))} tags")
            
            return parsed_response
            
        except Exception as e:
            logger.error(f"❌ Error tagging chunk with LLM: {str(e)}")
            return {"risk_tags": [], "explanation": f"Error: {str(e)}", "section_guess": "Misc"}

    def _ensure_tagged_index(self, es_client: Elasticsearch, index_name: str):
        """
        Create index with mapping for tagged documents if not exists.
        """
        if es_client.indices.exists(index=index_name):
            return
        
        body = {
            "mappings": {
                "properties": {
                    "doc_id":      {"type": "keyword"},
                    "chunk_id":    {"type": "integer"},
                    "text":        {"type": "text"},      # BM25
                    "section":     {"type": "keyword"},   # from LLM section_guess
                    "risk_tags":   {"type": "keyword"},   # ONLY tags (no scores)
                    "explanation": {"type": "text"},      # optional human-friendly reason
                    "timestamp":   {"type": "date"},      # when indexed
                    "file_name":   {"type": "keyword"},   # source file name
                    "file_type":   {"type": "keyword"}    # source file type
                }
            }
        }
        es_client.indices.create(index=index_name, body=body)
        logger.info(f"✅ Created tagged index: {index_name}")

    async def ingest_tagged_chunks(
        self,
        chunks: List[str],
        doc_id: str,
        file_name: str,
        file_type: str,
        index_name: str = "tagged_legal_docs"
    ) -> int:
        """
        Ingest text chunks with LLM-generated tags into Elasticsearch.
        
        Args:
            chunks: List of text chunks to process
            doc_id: Unique document identifier
            file_name: Original file name
            file_type: File type (.pdf, .txt, etc.)
            index_name: Elasticsearch index name
            
        Returns:
            Number of chunks successfully ingested
        """
        try:
            logger.info(f"🔄 Processing {len(chunks)} chunks for ingestion into {index_name}")
            
            # Create Elasticsearch client
            client_params = {
                "hosts": [self.es_url],
                "verify_certs": False
            }
            
            # Add API key authentication if provided
            if self.api_key:
                client_params["api_key"] = self.api_key
            
            es_client = Elasticsearch(**client_params)
            
            # Ensure index exists with proper mapping
            self._ensure_tagged_index(es_client, index_name)
            
            actions = []
            for i, chunk in enumerate(chunks, start=1):
                # Get LLM tags for this chunk
                llm_tags = await self.tag_chunk_with_llm(chunk)
                
                # Prepare document for indexing
                doc = {
                    "_index": index_name,
                    "_source": {
                        "doc_id": doc_id,
                        "chunk_id": i,
                        "text": chunk,
                        "section": llm_tags.get("section_guess", "Misc"),
                        "risk_tags": llm_tags.get("risk_tags", []),
                        "explanation": llm_tags.get("explanation", ""),
                        "timestamp": datetime.utcnow().isoformat(),
                        "file_name": file_name,
                        "file_type": file_type
                    }
                }
                actions.append(doc)
                
                logger.debug(f"📋 Prepared chunk {i}/{len(chunks)} with tags: {llm_tags.get('risk_tags', [])}")
            
            # Bulk index all documents
            if actions:
                try:
                    response = helpers.bulk(es_client, actions, raise_on_error=False, raise_on_exception=False)
                    
                    # Check response structure
                    if isinstance(response, tuple) and len(response) >= 2:
                        success_count, failed_docs = response
                        
                        if failed_docs:
                            logger.error(f"❌ {len(failed_docs)} documents failed to index:")
                            for i, doc in enumerate(failed_docs[:3]):  # Log first 3 failures
                                logger.error(f"Failed doc {i+1}: {doc}")
                            raise Exception(f"{len(failed_docs)} document(s) failed to index. First error: {failed_docs[0] if failed_docs else 'Unknown'}")
                        
                        logger.info(f"✅ Successfully ingested {success_count} tagged chunks into {index_name}")
                        
                    else:
                        # Different response format, assume success if no exception
                        logger.info(f"✅ Bulk operation completed for {len(actions)} documents")
                    
                    es_client.indices.refresh(index=index_name)
                    
                except Exception as bulk_error:
                    logger.error(f"❌ Bulk indexing error: {str(bulk_error)}")
                    raise Exception(f"Bulk indexing failed: {str(bulk_error)}")
            
            return len(actions)
            
        except Exception as e:
            logger.error(f"❌ Failed to ingest tagged chunks: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to ingest tagged chunks: {str(e)}"
            )

    def search_doc_by_tags_all(
        self,
        es: Elasticsearch,
        index_name: str,
        doc_id: str,
        tags: List[str],
        size: int = 10
    ) -> List[str]:
        """
        Retrieve texts for a specific doc_id that match ALL of the given tags.

        Args:
            es: Elasticsearch client
            index_name: index to search
            doc_id: the document ID to filter on
            tags: list of tag slugs to match (all must be present)
            size: max number of results

        Returns:
            list of matching chunk texts
        """
        try:
            logger.debug(f"🔍 Searching for doc_id '{doc_id}' with ALL tags: {tags}")
            
            # must contain doc_id
            must_filters = [{"term": {"doc_id": doc_id}}]

            # must contain each tag
            for tag in tags:
                must_filters.append({"term": {"risk_tags": tag}})

            query = {
                "size": size,
                "query": {
                    "bool": {
                        "must": must_filters
                    }
                },
                "_source": ["text"]
            }

            res = es.search(index=index_name, body=query)
            matching_texts = [hit["_source"]["text"] for hit in res["hits"]["hits"]]
            
            logger.info(f"✅ Found {len(matching_texts)} chunks matching all tags for doc_id '{doc_id}'")
            return matching_texts
            
        except Exception as e:
            logger.error(f"❌ Error searching by tags: {str(e)}")
            return []