from typing import List, Dict
from functools import lru_cache
import logging

from langchain_core.documents import Document
from langchain.vectorstores.pgvector import PGVector
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.schema.embeddings import Embeddings

from app.enums.env_keys import EnvKeys
from app.utils.utility_manager import UtilityManager
from app.databases.postgres_database_manager import PostgreManager
from app.dataclasses.vectorsearch_dataclass import VectorSearchResult


logger = logging.getLogger(__name__)

class PGVectorEmbeddingException(Exception):
    """Custome exception for vector embedding operations."""
    pass

class PGVectorEmbedding(UtilityManager):
    """Manages vector embeddings using PGVector and Google's Generative AI."""
    def __init__(self):
        """Initialize PGVector embedding manager."""
        super().__init__()
        self.db_manager = PostgreManager()

    def _initialize_config(self) -> None:
        """Initialize configuration from envirement variables."""
        try:
            self._api_key = self.get_env_variable(EnvKeys.GEMINI_API_KEY.value)
            self._model = self.get_env_variable(EnvKeys.GEMINI_EMBEDDING_MODEL.value)
        except ValueError as e:
            logger.error(f"Configuration error: {str(e)}")
            raise PGVectorEmbeddingException(f"Failed to configure: {str(e)}")

    @lru_cache()
    def _create_embedding_model(self):
        """Create and configure the embedding model.

        Returns:
            Embeddings: Configured embedding model

        Raises:
            PGVectorEmbeddingException: If model creation fails
        """
        try:
            return GoogleGenerativeAIEmbeddings(
                model=self._model,
                api_key=self._key
            )
        except Exception as e:
            logger.error(f"Failed to create embedding model: {str(e)}")
            raise PGVectorEmbeddingException(f"Failed to create embedding model: {str(e)}")
    
    def _get_vectorstor(self, collection_name: str = 'vectorstore') -> PGVector:
        """Get or create Vector store instance

        Args:
            collection_name: Name of the vector collection

        Returns:
            PGVector: istance of PG Vector
        """
        try:
            embedding_function = self._create_embedding_model()
            connection_string = self.db_manager._create_connection_url()

            return PGVector(
                embedding_function=embedding_function,
                collection_name=collection_name,
                connection_string=connection_string
            )
        except Exception as e:
            logger.error(f"Failed to initialize vector store: {str(e)}")
            raise PGVectorEmbeddingException(f"Failed to initialize vector store: {str(e)}")
    
    def create_vector_embeddings(
        self, 
        docs: List[Document], 
        collection_name: str = 'vectorstore'
        ) -> Dict[str, str]:
        """Create vector embeddings from documents

        Args:
            docs: List of Langchain Document 
            collection_name: name of vector store instance
        Returns:
            Dict[str, str]: Status message
        """
        try:
            vectorstore = self._get_vectorstor(collection_name)
            vectorstore.add_documents(documents=docs)

            msg = f"Embeddings created sucessfully for: {collection_name}"
            logger.info(msg)
            return {"message": msg}
        
        except Exception as e:
            logger.error(f"Embedding Creation Error: {str(e)}")
            raise PGVectorEmbeddingException(f"Failed to create Embedding: {str(e)}")
        
    def search_in_vector(
        self, 
        query:str, 
        collection_name:str = 'vectorstore',
        k:int = 3) -> VectorSearchResult:
        """Search for similar vectors in the collection.
        
        Args:
            query: Search query string
            collection_name: Name of the vector collection
            k: Number of results to return
            
        Returns:
            VectorSearchResult: Search results
        """
        try:
            vectorstore = self._get_vectorstor(collection_name=collection_name)
            results = vectorstore.similarity_search(query, k=k)

            return VectorSearchResult(
                message="Search Successfull",
                results=[doc.dict() for doc in results]
            )
        except Exception as e:
            logger.error(f"Vector search error: {str(e)}")
            raise PGVectorEmbeddingException(f"Search failed: {str(e)}")
    
    def delete_vector(self, collection_name:str) -> Dict[str, str]:
        """Delete a vector collection

        Args:
            collection_name: Name of the collection

        Returns:
            Dict[str, str]: Status message
        """
        try:
            vectorstore = self._get_vectorstor(collection_name=collection_name)
            vectorstore.delete_collection()

            msg = f"Collection {collection_name} deleted successfully"
            logger.info(msg)
            return {"message": msg}
        
        except Exception as e:
            logger.error(f"Vector deletion error: {str(e)}")
            raise PGVectorEmbeddingException(f"Failed to delete vector: {str(e)}")
        
    def cleanup(self) -> None:
        """Cleanup resources"""
        try:
            self.db_manager.cleanup()
        except Exception as e:
            logger.error(f"Cleanup error: {str(e)}")


        
