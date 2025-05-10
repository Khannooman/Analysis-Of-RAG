from typing import Dict, List, Any
from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema import LLMResult
import time

class TokenUsageCallbackHandler(BaseCallbackHandler):
    """Custom callback handler to track token usage and costs"""

    def __init__(self):
        super().__init__()
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.total_tokens = 0
        self.total_cost = 0.0
        self.start_time = None
        self.end_time = None

    def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], **kwargs) -> None:
        """Called when LLM starts running"""
        self.start_time = time.time()

    def on_llm_end(self, response: LLMResult, **kwargs) -> None:
        """Called when LLMs end running"""
        self.end_time = time.time()



    