from services.logging import get_logger, log_with_context
from services.llm_service import ask_question
from services.elastic_search_service import ElasticsearchService
from fastapi import APIRouter, Depends, HTTPException
from services.health_service import get_health_status
from langchain_aws import BedrockEmbeddings
from clients.aws_client import get_aws_bedrock_client
import os
import uuid

router = APIRouter(prefix="/health", tags=["Health"])

logger = get_logger("guardrail_service")

@router.get("/", summary="Health check", description="Returns OK if the service is alive")
async def health(status: dict = Depends(get_health_status)):
    return status

@router.get("/document-analysis")
async def get_document_analysis():
    """Return sample document analysis JSON"""
    return {
        "Document_Type": "Rental Agreement",
        "Main_Purpose": "To establish the terms and conditions for the rental of a residential property between a landlord and a tenant.",
        "Key_Highlights": [
            {
                "data": "11-month fixed term tenancy starting October 1, 2025."
            },
            {
                "data": "Monthly rent of ₹25,000 due by the 5th, with a steep ₹500/day late fee after 3 days."
            },
            {
                "data": "Refundable security deposit of ₹75,000, subject to deductions for unpaid rent, damages, or utilities."
            },
            {
                "data": "Either party can terminate with one-month written notice: early vacating without notice forfeits the deposit."
            }
        ],
        "Risk_Assessment": {
            "Risk_Score": 9,
            "High_Risk": [
                {
                    "title": "Steep Late Fee Penalty",
                    "description": "₹500/day late fee after 3 days is unusually high and may be unenforceable in court."
                },
                {
                    "title": "Deposit Forfeiture Clause",
                    "description": "Complete deposit forfeiture for early termination may be excessive and legally questionable."
                }
            ],
            "Medium_Risk": [
                {
                    "title": "Vague Maintenance Terms",
                    "description": "Minor repairs and major structural issues are not clearly defined."
                },
                {
                    "title": "Notice Period Ambiguity",
                    "description": "One-month notice requirement lacks specific delivery method requirements."
                }
            ]
        },
        "Key_Terms": [
            {
                "title": "Monthly Rent",
                "description": "₹25,000 Due by 5th of each month"
            },
            {
                "title": "Lease Duration",
                "description": "11 months Fixed term starting October 1, 2025"
            }
        ],
        "Suggested_Questions": [
            "What happens if I pay rent late?", 
            "Can I terminate the lease early?"
        ]
    }

@router.get("/test")
async def test_endpoint():
    return await ask_question(
        system_message="You are a helpful assistant that provides concise answers based on the user's input.",
        human_message="What is the capital of France?"
    )
    
@router.get("/test-guardrail")
async def test_guardrail_endpoint():
    from services.custom_guardrail_service import validate_user_question
    test_question = "Is it legal to download movies for free?"
    is_valid = await validate_user_question(test_question)
    if is_valid:
        logger.info(f"Guardrail validation passed for question: {test_question}")
    else:
        logger.warning(f"Guardrail validation failed for question: {test_question}")
    return {
        "question": test_question,
        "is_valid": is_valid
    }

@router.get("/test-embeddings")
async def test_embeddings_endpoint():
    from services.llm_service import get_embedding
    test_text = "Sample text for embedding"
    embedding = await get_embedding(test_text)
    if embedding:
        logger.info(f"Embedding generated successfully for text: {test_text}")
    else:
        logger.error(f"Failed to generate embedding for text: {test_text}")
    return {
        "text": test_text,
        "embedding": embedding,
        "embedding_length": len(embedding) if embedding else 0
    }

@router.get("/test-elasticsearch")
async def test_elasticsearch_ingestion():
    """Test Elasticsearch ingestion with mock data"""
    try:
        logger.info("🧪 Starting Elasticsearch ingestion test")
        
        # Get AWS client for embeddings
        aws_client = get_aws_bedrock_client()
        
        # Initialize Bedrock embeddings
        embeddings = BedrockEmbeddings(
            client=aws_client,
            model_id="cohere.embed-english-v3"
        )
        
        # Create Elasticsearch service
        es_service = ElasticsearchService(
            es_url=os.getenv('ELASTICSEARCH_URL', 'https://my-elasticsearch-project-b07525.es.us-central1.gcp.elastic.cloud:443'),
            api_key=os.getenv('ELASTICSEARCH_API_KEY', 'SVQ3Y1Y1a0JscUh2YzI0Rmlkd2Q6eTBMVHBudW14Wm53WjFydGM1SFVsZw=='),
            embedding_model=embeddings
        )
        
        # Mock test data
        test_chunks = [
            "The tenant shall pay monthly rent of $2,000 on the first day of each month. Late payments will incur a penalty of $50 per day.",
            "Either party may terminate this lease with 30 days written notice. Early termination by tenant forfeits security deposit.",
            "Landlord is responsible for major repairs. Tenant is responsible for minor maintenance and utilities."
        ]
        
        test_doc_id = str(uuid.uuid4())
        
        logger.info(f"🔄 Testing ingestion of {len(test_chunks)} mock chunks")
        
        # Test the ingestion
        ingested_count = await es_service.ingest_tagged_chunks(
            chunks=test_chunks,
            doc_id=test_doc_id,
            file_name="test_contract.txt",
            file_type=".txt",
            index_name="test_legal_docs"
        )
        
        logger.info(f"✅ Test ingestion completed successfully: {ingested_count} chunks")
        
        return {
            "success": True,
            "test_doc_id": test_doc_id,
            "chunks_tested": len(test_chunks),
            "chunks_ingested": ingested_count,
            "test_data": test_chunks,
            "index_name": "test_legal_docs",
            "message": "Elasticsearch ingestion test completed successfully"
        }
        
    except Exception as e:
        logger.error(f"❌ Elasticsearch test failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Elasticsearch test failed: {str(e)}"
        )

@router.get("/test-elasticsearch-simple")
async def test_elasticsearch_simple():
    """Simple test to check Elasticsearch connection and index creation"""
    try:
        logger.info("🧪 Starting simple Elasticsearch connection test")
        
        # Get AWS client for embeddings
        aws_client = get_aws_bedrock_client()
        
        # Initialize Bedrock embeddings
        embeddings = BedrockEmbeddings(
            client=aws_client,
            model_id="cohere.embed-english-v3"
        )
        
        # Create Elasticsearch service
        es_service = ElasticsearchService(
            es_url=os.getenv('ELASTICSEARCH_URL', 'https://my-elasticsearch-project-b07525.es.us-central1.gcp.elastic.cloud:443'),
            api_key=os.getenv('ELASTICSEARCH_API_KEY', 'SVQ3Y1Y1a0JscUh2YzI0Rmlkd2Q6eTBMVHBudW14Wm53WjFydGM1SFVsZw=='),
            embedding_model=embeddings
        )
        
        # Test connection by creating client
        from elasticsearch import Elasticsearch
        
        client_params = {
            "hosts": [es_service.es_url],
            "verify_certs": True
        }
        
        if es_service.api_key:
            client_params["api_key"] = es_service.api_key
        
        es_client = Elasticsearch(**client_params)
        
        # Test basic operations
        info = es_client.info()
        logger.info(f"✅ Elasticsearch connection successful: {info.get('cluster_name', 'Unknown')}")
        
        # Test index creation
        test_index = "simple_test_index"
        if es_client.indices.exists(index=test_index):
            es_client.indices.delete(index=test_index)
            logger.info(f"🗑️ Deleted existing test index: {test_index}")
        
        # Create simple index
        body = {
            "mappings": {
                "properties": {
                    "test_field": {"type": "text"},
                    "timestamp": {"type": "date"}
                }
            }
        }
        
        es_client.indices.create(index=test_index, body=body)
        logger.info(f"✅ Created test index: {test_index}")
        
        # Clean up
        es_client.indices.delete(index=test_index)
        logger.info(f"🗑️ Cleaned up test index: {test_index}")
        
        return {
            "success": True,
            "cluster_info": info,
            "test_index": test_index,
            "message": "Elasticsearch connection and basic operations successful"
        }
        
    except Exception as e:
        logger.error(f"❌ Simple Elasticsearch test failed: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Elasticsearch connection test failed"
        }

@router.get("/test-es-chunks")
async def test_elasticsearch_chunks():
    """Fetch all chunks from Elasticsearch index and display their metadata tags"""
    try:
        logger.info("🔍 Fetching all chunks from Elasticsearch index")
        
        # Get AWS client for embeddings
        aws_client = get_aws_bedrock_client()
        
        # Initialize Bedrock embeddings
        embeddings = BedrockEmbeddings(
            client=aws_client,
            model_id="cohere.embed-english-v3"
        )
        
        # Create Elasticsearch service
        es_service = ElasticsearchService(
            es_url=os.getenv('ELASTICSEARCH_URL', 'https://my-elasticsearch-project-b07525.es.us-central1.gcp.elastic.cloud:443'),
            api_key=os.getenv('ELASTICSEARCH_API_KEY', 'SVQ3Y1Y1a0JscUh2YzI0Rmlkd2Q6eTBMVHBudW14Wm53WjFydGM1SFVsZw=='),
            embedding_model=embeddings
        )
        
        # Create Elasticsearch client
        from elasticsearch import Elasticsearch
        
        client_params = {
            "hosts": [es_service.es_url],
            "verify_certs": True
        }
        
        if es_service.api_key:
            client_params["api_key"] = es_service.api_key
        
        es_client = Elasticsearch(**client_params)
        
        # Define the index name (you can change this if your index has a different name)
        index_name = "tagged_legal_docs"
        
        # Check if index exists
        if not es_client.indices.exists(index=index_name):
            logger.warning(f"⚠️ Index '{index_name}' does not exist")
            return {
                "success": False,
                "message": f"Index '{index_name}' does not exist",
                "total_chunks": 0,
                "chunks": []
            }
        
        logger.info(f"📊 Index '{index_name}' exists, fetching documents...")
        
        # Search for all documents (with size limit for safety)
        # Note: Using count query first to get total count (serverless compatible)
        count_body = {
            "query": {"match_all": {}}
        }
        
        try:
            count_response = es_client.count(index=index_name, body=count_body)
            total_docs = count_response['count']
            logger.info(f"📊 Found {total_docs} total documents in index '{index_name}'")
        except Exception as count_error:
            logger.warning(f"⚠️ Could not get document count (serverless mode): {str(count_error)}")
            total_docs = "Unknown (serverless mode)"
        
        search_body = {
            "query": {"match_all": {}},
            "size": 100,  # Limit to 100 docs for safety - can be increased
            "sort": [{"timestamp": {"order": "desc"}}],  # Sort by timestamp, newest first
            "_source": ["doc_id", "chunk_id", "text", "section", "risk_tags", "explanation", "timestamp", "file_name", "file_type"]
        }
        
        response = es_client.search(index=index_name, body=search_body)
        
        hits = response['hits']['hits']
        
        # Process and format the results
        chunks_data = []
        for hit in hits:
            source = hit['_source']
            chunk_info = {
                "elasticsearch_id": hit['_id'],
                "doc_id": source.get("doc_id", "N/A"),
                "chunk_id": source.get("chunk_id", "N/A"),
                "file_name": source.get("file_name", "N/A"),
                "file_type": source.get("file_type", "N/A"),
                "section": source.get("section", "N/A"),
                "risk_tags": source.get("risk_tags", []),
                "risk_tag_count": len(source.get("risk_tags", [])),
                "explanation": source.get("explanation", "N/A"),
                "timestamp": source.get("timestamp", "N/A"),
                "text_preview": source.get("text", "")[:200] + "..." if len(source.get("text", "")) > 200 else source.get("text", ""),
                "text_length": len(source.get("text", ""))
            }
            chunks_data.append(chunk_info)
        
        # Generate summary statistics
        total_risk_tags = sum(len(chunk.get("risk_tags", [])) for chunk in chunks_data)
        unique_risk_tags = set()
        sections_count = {}
        file_types_count = {}
        
        for chunk in chunks_data:
            unique_risk_tags.update(chunk.get("risk_tags", []))
            section = chunk.get("section", "Unknown")
            file_type = chunk.get("file_type", "Unknown")
            
            sections_count[section] = sections_count.get(section, 0) + 1
            file_types_count[file_type] = file_types_count.get(file_type, 0) + 1
        
        summary = {
            "total_chunks_in_index": total_docs,
            "chunks_retrieved": len(chunks_data),
            "total_risk_tags_applied": total_risk_tags,
            "unique_risk_tags_count": len(unique_risk_tags),
            "unique_risk_tags": sorted(list(unique_risk_tags)),
            "sections_breakdown": sections_count,
            "file_types_breakdown": file_types_count
        }
        
        logger.info(f"✅ Successfully retrieved {len(chunks_data)} chunks with metadata")
        
        return {
            "success": True,
            "index_name": index_name,
            "summary": summary,
            "chunks": chunks_data
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to fetch chunks from Elasticsearch: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch chunks from Elasticsearch: {str(e)}"
        )