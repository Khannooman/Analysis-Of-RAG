import pytest
from unittest.mock import patch, MagicMock
from app.llm.gemini_manager import GeminiManager, GeminiException

@pytest.fixture
def gemini_manager():
    with patch('app.llm.gemini_manager.GeminiManager._load_config'):
        return GeminiManager()

async def test_run_chain_success(gemini_manager):
    mock_response = MagicMock(content="Test response")
    mock_chain = MagicMock()
    mock_chain.ainvoke.return_value = mock_response

    with patch('app.llm.gemini_manager.RunnableSequence', return_value=mock_chain):
        result = await gemini_manager.run_chain(
            prompt_template=MagicMock(),
            input_values={"test": "value"}
        )
        
    assert result == "Test response"

async def test_run_chain_with_parser(gemini_manager):
    mock_response = MagicMock(content="Test response")
    mock_parser = MagicMock()
    mock_parser.parse.return_value = {"parsed": "data"}

    with patch('app.llm.gemini_manager.RunnableSequence') as mock_sequence:
        mock_sequence.return_value.ainvoke.return_value = mock_response
        result = await gemini_manager.run_chain(
            prompt_template=MagicMock(),
            input_values={"test": "value"},
            output_parser=mock_parser
        )
        
    assert "parsed" in result