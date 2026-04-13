import asyncio
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from app.services.chatbot_service import ChatBotService
from app.model.ChatResponse import ChatResponse
from app.model.ChatRequest import ChatRequest
from app.dependencies.chatbot_container import get_chatbot 
import json
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ChatController")

router = APIRouter(prefix="/chatbot", tags=["Chatbot"])
@router.post("/sendMessage") 
async def chatbot(
    request: ChatRequest,
    bot: ChatBotService = Depends(get_chatbot)
):
    logger.info(
        "Controller received chat request for userId=%s history_count=%s",
        request.userId,
       len(request.historyMessageList or []),
     )
    try:
        if not request.message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        try:
            response_data = await bot.process_query(request.message, request.userId)
        
            return response_data
        except Exception as e:
            logger.error(f"Error in streaming response: {e}")
            raise HTTPException(status_code=500, detail="Error processing the request")

    except Exception as e:
        logger.error(f"Error in controller: {e}")
        raise HTTPException(status_code=500, detail=str(e))