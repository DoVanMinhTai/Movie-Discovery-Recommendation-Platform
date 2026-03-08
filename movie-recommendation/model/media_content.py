from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.orm import relationship
from config.config import Settings

DATABASE_URL = Settings().database_url

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit= False, bind=engine, autoflush=False)
Base = declarative_base()

mediacontent_genres = Table(
    "mediacontent_genres",
    Base.metadata,
    Column("mediacontent_id", Integer, ForeignKey("mediacontent.movie_id"), primary_key=True),
    Column("genre_id", Integer, ForeignKey("genres.id"), primary_key=True),
)

class Genre(Base):
    __tablename__ = "genres"
    id = Column(Integer, primary_key=True)
    name = Column(String)

class Movie(Base):
    __tablename__ = "mediacontent"
    id = Column("movie_id",Integer, primary_key=True)
    title = Column(String)
    genres = relationship("Genre", secondary=mediacontent_genres)