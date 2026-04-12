import asyncio
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from app.services.chatbot_service import ChatBotService
from app.model.ChatResponse import ChatResponse
from app.model.ChatRequest import ChatRequest
from app.dependencies.chatbot_container import get_chatbot 
import json

router = APIRouter(prefix="/chatbot", tags=["Chatbot"])
@router.post("/sendMessage") 
async def chatbot(
    request: ChatRequest,
    bot: ChatBotService = Depends(get_chatbot)
):
    try:
        if not request.message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        async def token_generator():
            try:
                async for token in bot.process_query_stream(request.message, request.userId):
                    yield f"data: {json.dumps(token, ensure_ascii=False)}\n\n"  
                    await asyncio.sleep(0.01)  
            
            except Exception as e:
                error = {"error": str(e)}
                yield json.dumps(error) + "\n"
                        
        return StreamingResponse(token_generator(), media_type="text/event-stream")
    except Exception as e:
        print(f"Error in controller: {e}")
        raise HTTPException(status_code=500, detail=str(e))