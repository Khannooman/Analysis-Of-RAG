from datetime import datetime
from typing import Dict, List, Optional, Union
import logging

from app.databases.postgres_database_manager import PostgreManager
from app.llm.gemini_manager import GeminiManager
from app.models.chat_request_model import ChatRequestModel
from app.models.response_model import ResponseModel
from app.utils.utility_manager import UtilityManager


logger = logging.getLogger(__name__)

class ConversationChatControllerException(Exception):
    """Raise customized exceptiion for ConversationChatController"""


class ConversationChatController(UtilityManager):
    """Conversational Chat Controller which controll the conversation between AI and User"""
    
    def __init__(self):
        """Initialized the Conversational Chat controllers"""
        super().__init__()
        self.db = PostgreManager()
        self.MODEL = GeminiManager()

    async def conversational_chat(self, request: ChatRequestModel) -> ResponseModel:
        """Handle conversational chat requests and generate appropriate response

        Args:
            request: ChatResquestModel contaning attribute of rquests
        
        Returns:
            ResponseModel: Model response with all the metadata
        
        Raise:
            ConversationChatControllerException
        """
        start_time = datetime.now()

        try:
            # validating user_id
            if not hasattr(request, "user_id"):
                logger.error(f"user_id not present in the request")
                raise ConversationChatControllerException(f"user_id not present in the request")
            
            user_id = request.user_id
            logger.info(f"Processing chat request for user_id: {user_id}")

            # Fetch use hi



