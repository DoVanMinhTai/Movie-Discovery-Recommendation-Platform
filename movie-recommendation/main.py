from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager
import uvicorn
from common.database import Base, engine
from utils.ml_utils import load_content_model, load_collaborative_model
from controller import recommend_controller, admin_controller, retraining_controller
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.ml_models = {
        "content_based_filtering": load_content_model(),
        "collaborative_filtering": load_collaborative_model()
        }
    yield
    app.state.ml_models.clear()
    
app = FastAPI(lifespan=lifespan)

app.include_router(router=recommend_controller.router)
app.include_router(router=admin_controller.router)
app.include_router(router=retraining_controller.router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)