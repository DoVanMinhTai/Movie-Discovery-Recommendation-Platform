from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.controller import chat_controller as chat_controller
from app.dependencies import chatbot_container as chatbot_container 
from app.services.chatbot_service import ChatBotService

@asynccontextmanager
async def lifespan(app: FastAPI):
    chatbot_container.chatbot_instance = ChatBotService()
    yield
    chatbot_container.chatbot_instance = None

app = FastAPI(lifespan=lifespan, title="Movie Recommendation Chatbot")

app.include_router(chat_controller.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    print(f"❌ Chi tiết lỗi 422: {exc.errors()}") 
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "body": exc.body},
    )