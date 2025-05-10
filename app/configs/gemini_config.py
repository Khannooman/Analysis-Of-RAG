from dataclasses import dataclass

@dataclass
class GeminiConfig:
    """Configuration for Gemini LLM."""
    api_key: str
    temperature: float
    model: str
    verbose: bool
    timeout: int
    max_retries: int