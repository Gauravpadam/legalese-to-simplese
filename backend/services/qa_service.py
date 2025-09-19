"""
QA Service for handling user questions and providing answers.
"""

from typing import Dict, Any, List, Tuple
from services.custom_guardrail_service import validate_user_question
from clients.ollama import OllamaClient
from services.elastic_search_service import ElasticsearchService

import json


async def process_user_question(question: str = "What is the related risk to the contract", doc_id: str = "e859e40d-f6be-41d2-80e7-14d272805953") -> Dict[str, Any]:
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
    
    # Step 2: Pass the cleaned question to custom guardrail service
    is_question_valid = await validate_user_question(cleaned_question)

    # Step 3: If question valid, we proceed
  
    if not is_question_valid:
        raise Exception("Your query violates policies")


    chunks = await elasticService.search_documents(question)

    # Now we use the relevant doc chunks and the question to get a final answer
    if chunks and 'content' in chunks:
        context = chunks['content']
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

    # Parse the JSON response
    try:
        response_json = json.loads(response_text)
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON response from LLM")

    # Extract the final answer
    final_answer = response_json.get("answer", "No answer found.")
    return {
        "question": question,
        "final_answer": final_answer,
        "chunks": chunks,
    }


async def main():
    """Main function to run the QA service."""
    try:
        result = await process_user_question()
        print("QA Service Result:")
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"Error running QA service: {e}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())