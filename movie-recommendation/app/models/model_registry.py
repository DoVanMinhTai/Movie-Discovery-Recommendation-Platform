from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, Mapped, mapped_column
from datetime import datetime, timezone
from sqlalchemy import create_engine
from typing import List, Optional
from pydantic import BaseModel
from config.config import Settings

DATABASE_URL = Settings().database_url

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit= False, bind=engine, autoflush=False)
Base = declarative_base()

class Training_Jobs_Logs(Base):
    __tablename__ = "training_jobs_logs"

    id = Column(String, primary_key=True, index=True)
    job_status = Column(String, default="PENDING")  
    
    content_based_time = Column(DateTime, nullable=True)
    colleborating_time = Column(DateTime, nullable=True)
    
    error_message = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Model_Registry(Base):
    __tablename__ = "model_registry"

    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String)
    version = Column(Float)
    model_path = Column(String)     
    rmse = Column(Float)           
    mae = Column(Float)
    precision = Column(Float)
    recall = Column(Float)
    f1_score = Column(Float)
    is_active: Mapped[bool] = mapped_column(default=True)    
    job_id = Column(String, ForeignKey(column="training_jobs_logs.id"), nullable=True)
    created_at = datetime.now(timezone.utc).replace(tzinfo=None)
    
class RecommendationItem(BaseModel):
    movie_id: int
    score: float

class RecommendationResponse(BaseModel):
    strategy: str
    data: List[RecommendationItem]
    
class UserContext(BaseModel):
    user_Id: Optional[int] = None
    selected_Genres: Optional[List[str]] = None
    is_new_user: bool = True