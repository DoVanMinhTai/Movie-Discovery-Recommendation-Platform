from pydantic import BaseModel, Field
from typing import List, Optional

class HistoryMessage(BaseModel):
    # role: str      # 'user' hoặc 'bot'
    # content: str
    message: str

class ChatRequest(BaseModel):
    userId: Optional[int] = Field(default=0)
    message: str = Field()
    historyMessageList: Optional[List[HistoryMessage]] = Field(default_factory=list)