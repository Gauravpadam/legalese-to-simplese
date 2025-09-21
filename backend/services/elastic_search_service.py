import logging
import json
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from clients.ollama import OllamaClient
from langchain_elasticsearch import ElasticsearchStore
from langchain_community.embeddings import OllamaEmbeddings
from langchain.schema import Document
from fastapi import HTTPException
from elasticsearch import Elasticsearch, helpers

# Setup logger for this module
logger = logging.getLogger("elasticsearch_service")

class ElasticsearchService:
    """
    Service class to handle Elasticsearch operations including document ingestion and retrieval.
    """

    _elasticSearchStore = None
    _vector_store = None
    
    def __init__(self, es_url: str = "http://localhost:9200"):
        """
        Initialize the Elasticsearch service.
        
        Args:
            embedding_model: The embedding model to use for vectorization
            es_url: Elasticsearch URL (default: http://localhost:9200)
            api_key: API key for Elasticsearch authentication
        """
        self.embedding_model = OllamaClient.get_embedding_client() # This wont change unless the programmer changes it
        self.es_url = es_url
        logger.info(f"🔧 Initialized ElasticsearchService with URL: {es_url}")
    
    def create_vector_store(self, index_name: str = "doc_index") -> ElasticsearchStore:
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
            
            # # Add API key authentication if provided
            # if self.api_key:
            #     connection_params["es_api_key"] = self.api_key
            
            if not self._elasticSearchStore:
                self._elasticSearchStore = ElasticsearchStore(**connection_params)
                logger.info(f"✅ Vector store created successfully for index: {index_name}")
            
            return self._elasticSearchStore
        except Exception as es_error:
            logger.error(f"❌ Failed to create vector store: {str(es_error)}")
            raise HTTPException(
                status_code=503, 
                detail=f"ElasticSearch connection failed: {str(es_error)}"
            )
    
    def ingest_documents(self, documents: List[Document], index_name: str = "doc_index") -> Dict[str, Any]:
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
    
    def get_retriever(self, index_name: str = "doc_index", search_kwargs: Optional[Dict] = None):
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
            
            # Keeping this in JUST BECAUSE search kwargs may change sometime
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
    
    def search_documents(self, query: str, index_name: str = "doc_index", k: int = 4) -> List[Document]:
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
    
    # Good to have (currently useless)

    # def get_index_info(self, index_name: str = "workplace_index") -> Dict[str, Any]:
    #     """
    #     Get information about an Elasticsearch index.
        
    #     Args:
    #         index_name: Name of the Elasticsearch index (default: workplace_index)
            
    #     Returns:
    #         Dict containing index information
    #     """
    #     try:
    #         logger.debug(f"📊 Getting info for index: {index_name}")
            
    #         # Create vector store to access Elasticsearch client
    #         vector_store = self.create_vector_store(index_name)
            
    #         # This is a simplified version - you might want to expand this
    #         # to get actual index statistics from the Elasticsearch client
    #         info = {
    #             "index_name": index_name,
    #             "es_url": self.es_url,
    #             "status": "connected"
    #         }
            
    #         logger.info(f"✅ Retrieved info for index: {index_name}")
    #         return info
            
    #     except Exception as info_error:
    #         logger.error(f"❌ Failed to get index info: {str(info_error)}")
    #         return {
    #             "index_name": index_name,
    #             "es_url": self.es_url,
    #             "status": "error",
    #             "error": str(info_error)
    #         }