from fastapi import APIRouter, BackgroundTasks, Depends, FastAPI
from requests import Session
from utils.ml_utils import load_model_latest
from model.model_registry import Training_Jobs_Logs
from common.database import get_db, SessionLocal
from services.training_service import ReTrainingService

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.post("/reload-Model")
def refresh_model():
    app = FastAPI()
    app.state.ml_models = {"recommender": load_model_latest()}
    if not app.state.ml_models["recommender"]:
        print("WARNING: Application starting without a trained ML model.")
        yield
        app.state.ml_models.clear()
        return {"status": "Failed to load model"}
    return {"status": "Loaded Model"}

@router.get("/")
def read_root(db: Session = Depends(get_db)):
    return {"message": "Connected to PostgreSQL!"}

# Background Tasks
@router.post("/retrainingmodel")
async def retraining_model(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    import uuid
    job_id = str(uuid.uuid4())
    train_model = ReTrainingService(db).train_model
    background_tasks.add_task(train_model,job_id)
    return {"message": "Model retraining started", "job_id": job_id}

@router.get("/retrainingmodel/status/{job_id}")
def get_retraining_status(job_id: str):
    db = SessionLocal()
    job = db.query(Training_Jobs_Logs).filter(Training_Jobs_Logs.id == job_id).first()
    if job:
        return {
            "job_id": job.id,
            "status": job.job_status,
            "collaborative_time": job.collaborative_time,
            "content_based_time": job.content_based_time,
            "total_time": job.total_time,
            "error_message": job.error_message
        }
    return {"error": "Job ID not found"}