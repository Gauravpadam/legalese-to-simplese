from langchain_community.chat_models.ollama import ChatOllama
from langchain_community.embeddings import OllamaEmbeddings

class OllamaClient:

    _client = None
    _embedding_client = None

    @classmethod
    def get_client(cls):
        if not cls._client:
            cls._client = ChatOllama(model="llama3.1")
        return cls._client
    
    @classmethod
    def get_embedding_client(cls):
        if not cls._embedding_client:
            cls._embedding_client = OllamaEmbeddings(model="nomic-embed-text")
        return cls._embedding_client


