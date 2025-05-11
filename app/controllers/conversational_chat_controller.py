from datetime import datetime
from typing import Dict, List, Optional, Union
import logging

from app.databases.postgres_database_manager import PostgreManager
from app.llm.gemini_manager import GeminiManager
from app.models.chat_request_model import ChatRequestModel
from app.models.response_model import ResponseModel