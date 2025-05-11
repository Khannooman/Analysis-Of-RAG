from typing import Dict, List, Optional
from pydantic import BaseModel, Field

class ChatRequestModel(BaseModel):
    question: str = Field(..., description="The question or query for which data is being requested.")
    context: Optional[str] = Field(None, description="Context for the question")
    return_history: bool = False
    