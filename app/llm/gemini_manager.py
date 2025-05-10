from dataclasses import dataclass
from typing import Dict, Union, Any, Optional
import logging
import os
from functools import lru_cache

from langchain_google_genai.chat_models import ChatGoogleGenerativeAI
from langchain.output_parsers import StructuredOutputParser
from langchain.prompts import PromptTemplate
from langchain.schema.runnable import RunnableSequence
from langchain_core.messages import AIMessage

from app.utils.utility_manager import UtilityManager
from app.enums.env_keys import EnvKeys
from app.utils.calculate_token_usage import calculate_token
from app.configs.gemini_config import GeminiConfig

logger = logging.getLogger(__name__)

class GeminiException(Exception):
    """Custom exception for gemini-related errors"""
    pass

class GeminiManager(UtilityManager):
    """Manages intractions with Google's Gemini LLM using LangChain"""

    _instance: Optional['GeminiManager'] = None

    def __new__(cls) -> 'GeminiManager':
        """Implement singleton pattern"""
        if cls._instance is None:
            cls._instance = super().__init__(cls)
        return cls._instance
    
    def __init__(self) -> None:
        """Initialize GeminiManager with configuration."""
        if hasattr(self, 'initialized'):
            return 
        
        super().__init__()
        self.initialized = True
        self.config = self._load_config()

    @lru_cache()
    def _load_config(self) -> GeminiConfig:
        """Load and validate Gemini configuration"""
        try:
            return GeminiConfig(
                api_key=self.get_env_variable(EnvKeys.GEMINI_API_KEY.value),
                temperature=self.get_env_variable(EnvKeys.GEMINI_TEMPERATURE.value),
                model=self.get_env_variable(EnvKeys.GEMINI_MODEL.value),
                verbose=self.get_env_variable(EnvKeys.GEMINI_VERBOSE.value),
                timeout=self.get_env_variable(EnvKeys.GEMINI_TIMEOUT.value),
                max_retries=self.get_env_variable(EnvKeys.GEMINI_MAX_RETRIES.value)
            )
        except (ValueError, TypeError) as e:
            raise GeminiException(f"Invalid configuration: {str(e)}")
        
    def _create_llm_model(self) -> ChatGoogleGenerativeAI:
        """Create and configure LLM model instance"""
        return ChatGoogleGenerativeAI(
            model=self.config.model,
            temperature=self.config.temperature,
            api_key=self.config.api_key,
            verbose=self.config.verbose,
            timeout=self.config.timeout,
            max_retries=self.config.max_retries
        )
    
    def _process_response(
        self,
        response: AIMessage,
        output_parser: Optional[StructuredOutputParser]
    ) -> Union[Dict[str, Any], str]:
        """Process LLM response with optional parsing"""
        text_response = response.content if hasattr(response, 'content') else response
        token_usage = calculate_token(response=response)

        if not output_parser:
            return text_response
        
        try:
            result = output_parser.parse(text_response)
            result.update(token_usage)
            return result
        except Exception as e:
            logger.error(f"Errro parsing LLM Response: {str(e)}")
            raise GeminiException(f"Response parsing failed: {str(e)}")


    async def run_chain(
            self, 
            prompt_template: PromptTemplate, 
            output_parser: StructuredOutputParser = None,
            input_values: Dict = {}
            ) -> Union[dict, str]:
        """
        Exexute LLM chain with provided prompt

        Args:
            prompt_template: Template for generation prompt
            input_values: Values to populate the prompt template
            output_parser: Optional parser for structured output parser

        Returns:
            Union[Dict[str, Any], str]: Parsed response or raw text

        Raises:
            GeminiException: For LLM-related errors
        """
        try:
            llm_model = self._create_llm_model()
            chain = RunnableSequence(prompt_template | llm_model)
            
            logger.debug(f"Executing chain with inputs: {input_values}")
            response = await chain.ainvoke(input_values)

            return self._process_response(response, output_parser)
         
        except Exception as e:
            logging.error(f"Chain execution failed: {str(e)}")
            raise GeminiException(f"Chain execution failed: {str(e)}")

