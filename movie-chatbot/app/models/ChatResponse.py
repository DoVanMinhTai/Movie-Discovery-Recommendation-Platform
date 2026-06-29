from pydantic import BaseModel
from typing import  Any

class ChatResponse(BaseModel):
    intent: str
    message: str
    data: Any
    
    