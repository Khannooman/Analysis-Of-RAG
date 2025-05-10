from typing import Dict, TypedDict, Optional
from langchain_core.messages import AIMessage
import logging

logger = logging.getLogger(__name__)

def calculate_token(response: AIMessage) -> Dict[str, int]:
    """
    Calculate token usage from an AI message response.
    
    Args:
        response (AIMessage): The AI message response containing usage metadata
        
    Returns:
        Dict[str, int]: Dictionary containing token usage statistics
        
    Example:
        >>> response = AIMessage(content="Hello", usage_metadata={"input_tokens": 1, "output_tokens": 1, "total_tokens": 2})
        >>> calculate_token(response)
        {'input_tokens': 1, 'output_tokens': 1, 'total_tokens': 2}
    """
    try:
        if hasattr(response, 'usage_metadata') and response.usage_metadata:
            usage_metadata = response.usage_metadata
            return {
                'input_tokens': int(usage_metadata.get('input_tokens', 0)),
                'output_tokens': int(usage_metadata.get('output_tokens', 0)),
                'total_tokens': int(usage_metadata.get('total_tokens', 0))
            }
        
    except Exception as e:
        logger.error(f"Error calculating token usage: {str(e)}")
        return {
            'input_tokens': 0,
            'output_tokens': 0,
            'total_tokens': 0
        }