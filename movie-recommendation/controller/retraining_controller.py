import uuid
from fastapi import APIRouter, Depends, BackgroundTasks
from services.training_service import ReTrainingService
from common.database import get_db

router = APIRouter(prefix= "/training", tags=["Training"])

@router.get("/retraining")
def retraining_model(background_tasks: BackgroundTasks, db=Depends(get_db)): 
    job_id = str(uuid.uuid4())
    
    background_tasks.add_task(ReTrainingService(db).train_model, job_id)

    return {"status": "started", "job_id": job_id}