from typing import Optional
from app.services.nlp_service import NLPService

chatbot_instance: Optional[NLPService] = None

def get_chatbot() -> NLPService:
    if chatbot_instance is None:
        raise RuntimeError("Chatbot has not been initialized in lifespan!")
    return chatbot_instance