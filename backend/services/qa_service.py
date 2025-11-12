"""
QA Service for handling user questions and providing answers.
"""

from typing import Dict, Any, List, Tuple
from services.custom_guardrail_service import validate_user_question
from clients.ollama import OllamaClient
from services.elastic_search_service import ElasticsearchService
from DTO.DTO import QuestionResponse

import json


async def process_user_question(question: str = "What is the related risk to the contract") -> QuestionResponse:
    """
    Processes a user question through guardrail validation.
    
    Args:
        question (str): The user's question
        
    Returns:
        Dict[str, Any]: A dictionary containing the processed question, validation result and metadata
    """

    elasticService = ElasticsearchService(es_url="http://localhost:9200")

    
    # Clean and normalize the question
    cleaned_question = question.strip()
    
    # # Step 2: Pass the cleaned question to custom guardrail service
    # is_question_valid = await validate_user_question(cleaned_question)

    # Step 3: If question valid, we proceed
  
    # if not is_question_valid:
    #     raise Exception("Your query violates policies")


    chunks = elasticService.search_documents(question)

    # Now we use the relevant doc chunks and the question to get a final answer
    chunked_text = []
    if chunks:
        context = """<context>\n"""
        for chunk in chunks:
            context+=chunk.page_content
            chunked_text.append(chunk.page_content)
        context+="</context>"
    else:
        context = "No relevant document content found."

    final_system_prompt = (
        "You are a helpful AI assistant. Use the following context to answer questions accurately and helpfully:\n\n"
        f"Context: {context}\n\n"
        "Please provide clear, accurate, and helpful responses based on this context."
    )

    # Call Bedrock LLM to get the final answer
    messages = [
        {"role": "system", "content": final_system_prompt},
        {"role": "user", "content": cleaned_question}
    ]

    model = OllamaClient.get_client()

    response = await model.ainvoke(messages)

    response_text = response.content

    print(type(response_text))

    # Extract the final answer
    final_answer = response_text
    return QuestionResponse(question=question, answer=response_text, status="success")