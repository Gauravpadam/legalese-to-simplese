import time
from langchain_core.messages import HumanMessage, SystemMessage
from clients.ollama import OllamaClient
from services.logging import get_logger, log_with_context
from typing import List

logger = get_logger("llm_service")



async def ask_question(system_message: str, human_message: str, custom_instance = None):
    """
    Ask a question to the LLM with system and human messages.
    
    Args:
        system_message: System prompt/context
        human_message: User's question
        
    Returns:
        str: LLM response text
    """
    start_time = time.time()
    
    logger.info("Starting LLM question request")
    # logger.debug(f"System message length: {len(system_message)} chars")
    # logger.debug(f"Human message length: {len(human_message)} chars")
    
    try:
        # bedrock_client = get_aws_bedrock_client()
        # logger.debug("AWS Bedrock client obtained successfully")
        
        # model = ChatBedrock(
        #                 model_id="anthropic.claude-3-5-sonnet-20241022-v2:0",
        #                 # max_tokens=8192,
        #                 client=bedrock_client,
        #                 streaming=False,
        #             )

        if not custom_instance:
            model = OllamaClient.get_client()
        else:
            model = custom_instance
        
        logger.debug("Llama model initialized")
        logger.info("Received system message: {}".format(system_message))
        logger.info("Received system message: {}".format(human_message))
        
        messages = [SystemMessage(content=system_message),
                    HumanMessage(content=human_message)]

        
        logger.info("Invoking LLM model...")
        response = await model.ainvoke(messages)
        response_text = response.content
        
        duration = time.time() - start_time
        
        log_with_context(
            "llm_service",
            "info",
            "LLM question completed successfully",
            model_id="gpt-oss:cloud",
            system_msg_length=len(system_message),
            human_msg_length=len(human_message),
            response_length=len(response_text) if response_text else 0,
            duration_seconds=round(duration, 3),
            max_tokens=8192
        )
        
        return response_text
        
    except Exception as e:
        duration = time.time() - start_time
        
        log_with_context(
            "llm_service",
            "error",
            f"LLM question failed: {str(e)}",
            model_id="llama3.1",
            system_msg_length=len(system_message),
            human_msg_length=len(human_message),
            duration_seconds=round(duration, 3),
            error_type=type(e).__name__
        )
        
        logger.error(f"Error in ask_question: {e}", exc_info=True)
        raise

async def get_embedding(text):
    """
    Get text embedding using Bedrock embeddings model.
    
    Args:
        text: Text to embed
        
    Returns:
        list: Embedding vector
    """
    start_time = time.time()
    original_text_length = len(text)
    
    logger.info("Starting text embedding request")
    logger.debug(f"Original text length: {original_text_length} chars")
    
    try:
        embedding_model = OllamaClient.get_embedding_client()
        
        # Clean text
        text = text.replace("\n", " ")
        cleaned_text_length = len(text)
        
        if cleaned_text_length != original_text_length:
            logger.debug(f"Text cleaned, new length: {cleaned_text_length} chars")
        
        
        logger.debug("OllamaEmbeddings model initialized")
        
        logger.info("Generating embedding...")
        response = embedding_model.embed_query(text)
        
        duration = time.time() - start_time
        embedding_dimension = len(response) if response else 0
        
        log_with_context(
            "llm_service",
            "info",
            "Text embedding completed successfully",
            model_id="nomic-embed-text",
            original_text_length=original_text_length,
            cleaned_text_length=cleaned_text_length,
            embedding_dimension=embedding_dimension,
            duration_seconds=round(duration, 3)
        )
        
        return response
        
    except Exception as e:
        duration = time.time() - start_time
        
        log_with_context(
            "llm_service",
            "error",
            f"Text embedding failed: {str(e)}",
            model_id="nomic-embed-text",
            original_text_length=original_text_length,
            duration_seconds=round(duration, 3),
            error_type=type(e).__name__
        )
        
        logger.error(f"Error in get_embedding: {e}", exc_info=True)
        raise