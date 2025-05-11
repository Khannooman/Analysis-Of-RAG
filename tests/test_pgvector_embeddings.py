import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import List, Dict

from langchain_core.documents import Document
from langchain.vectorstores.pgvector import PGVector

from app.Embeddings.pgvector_embeddings import (
    PGVectorEmbedding,
    PGVectorEmbeddingException,
    VectorSearchResult
)

@pytest.fixture
def mock_env_variables():
    """Fixture to mock environment variables."""
    return {
        "GEMINI_API_KEY": "test-api-key",
        "GEMINI_EMBEDDING_MODEL": "test-model"
    }

@pytest.fixture
def pgvector_embedding(mock_env_variables):
    """Fixture to create PGVectorEmbedding instance with mocked dependencies."""
    with patch('app.Embeddings.pgvector_embeddings.PostgreManager'), \
         patch('app.Embeddings.pgvector_embeddings.GoogleGenerativeAIEmbeddings'), \
         patch.dict('os.environ', mock_env_variables):
        embedding = PGVectorEmbedding()
        embedding._api_key = mock_env_variables["GEMINI_API_KEY"]
        embedding._model = mock_env_variables["GEMINI_EMBEDDING_MODEL"]
        return embedding

@pytest.fixture
def mock_documents():
    """Fixture to create test documents."""
    return [
        Document(page_content="Test document 1", metadata={"source": "test1"}),
        Document(page_content="Test document 2", metadata={"source": "test2"})
    ]

def test_initialization(pgvector_embedding):
    """Test successful initialization of PGVectorEmbedding."""
    assert isinstance(pgvector_embedding, PGVectorEmbedding)
    assert hasattr(pgvector_embedding, 'db_manager')
    assert pgvector_embedding._api_key == "test-api-key"
    assert pgvector_embedding._model == "test-model"

def test_create_embedding_model(pgvector_embedding):
    """Test embedding model creation."""
    with patch('app.Embeddings.pgvector_embeddings.GoogleGenerativeAIEmbeddings') as mock_embeddings:
        mock_embeddings.return_value = Mock()
        model = pgvector_embedding._create_embedding_model()
        assert model is not None
        mock_embeddings.assert_called_once_with(
            model=pgvector_embedding._model,
            api_key=pgvector_embedding._api_key
        )

def test_get_vectorstore(pgvector_embedding):
    """Test vector store initialization."""
    with patch('app.Embeddings.pgvector_embeddings.PGVector') as mock_pgvector, \
         patch.object(pgvector_embedding, '_create_embedding_model') as mock_model:
        
        mock_model.return_value = Mock()
        mock_pgvector.return_value = Mock()
        
        vectorstore = pgvector_embedding._get_vectorstor("test_collection")
        
        assert vectorstore is not None
        mock_pgvector.assert_called_once()

@pytest.mark.asyncio
async def test_create_vector_embeddings(pgvector_embedding, mock_documents):
    """Test creating vector embeddings."""
    with patch.object(pgvector_embedding, '_get_vectorstor') as mock_vectorstore:
        mock_instance = Mock()
        mock_vectorstore.return_value = mock_instance
        
        result = pgvector_embedding.create_vector_embeddings(
            docs=mock_documents,
            collection_name="test_collection"
        )
        
        assert isinstance(result, dict)
        assert "message" in result
        mock_instance.add_documents.assert_called_once_with(documents=mock_documents)

def test_search_in_vector(pgvector_embedding):
    """Test vector similarity search."""
    mock_docs = [Document(page_content="Test result", metadata={"source": "test"})]
    
    with patch.object(pgvector_embedding, '_get_vectorstor') as mock_vectorstore:
        mock_instance = Mock()
        mock_instance.similarity_search.return_value = mock_docs
        mock_vectorstore.return_value = mock_instance
        
        result = pgvector_embedding.search_in_vector(
            query="test query",
            collection_name="test_collection",
            k=1
        )
        
        assert isinstance(result, VectorSearchResult)
        assert result.message == "Search Successfull"
        assert len(result.results) == 1
        mock_instance.similarity_search.assert_called_once_with("test query", k=1)

def test_delete_vector(pgvector_embedding):
    """Test vector collection deletion."""
    with patch.object(pgvector_embedding, '_get_vectorstor') as mock_vectorstore:
        mock_instance = Mock()
        mock_vectorstore.return_value = mock_instance
        
        result = pgvector_embedding.delete_vector("test_collection")
        
        assert isinstance(result, dict)
        assert "message" in result
        mock_instance.delete_collection.assert_called_once()

def test_cleanup(pgvector_embedding):
    """Test cleanup operation."""
    pgvector_embedding.db_manager = Mock()
    pgvector_embedding.cleanup()
    pgvector_embedding.db_manager.cleanup.assert_called_once()

def test_error_handling(pgvector_embedding):
    """Test error handling in various operations."""
    with patch.object(pgvector_embedding, '_get_vectorstor') as mock_vectorstore:
        mock_vectorstore.side_effect = Exception("Test error")
        
        with pytest.raises(PGVectorEmbeddingException):
            pgvector_embedding.create_vector_embeddings([], "test")
            
        with pytest.raises(PGVectorEmbeddingException):
            pgvector_embedding.search_in_vector("test")
            
        with pytest.raises(PGVectorEmbeddingException):
            pgvector_embedding.delete_vector("test")