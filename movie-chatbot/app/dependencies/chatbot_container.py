from typing import Optional
from app.services.chatbot_service import ChatBotService

chatbot_instance: Optional[ChatBotService] = None

def get_chatbot() -> ChatBotService:
    if chatbot_instance is None:
        raise RuntimeError("Chatbot has not been initialized in lifespan!")
    return chatbot_instance