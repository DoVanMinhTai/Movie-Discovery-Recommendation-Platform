from typing import List, Optional
from pydantic import BaseModel, Field, validator
from datetime import datetime


class RecommendationItem(BaseModel):
    movie_id: int = Field(..., description="Movie ID", ge=1)
    title: str = Field(..., description="Movie title")
    genres: str = Field("", description="Pipe-separated genres (e.g., 'Action|Sci-Fi')")
    score: float = Field(..., description="Recommendation score", ge=0)
    
    class Config:
        json_schema_extra = {
            "example": {
                "movie_id": 260,
                "title": "Star Wars: Episode IV - A New Hope (1977)",
                "genres": "Action|Adventure|Sci-Fi",
                "score": 0.95
            }
        }

class MovieSimilarResponse(BaseModel):
    movie_id: int = Field(..., description="Target movie ID")
    movie_title: str = Field(..., description="Target movie title")
    recommendations: List[RecommendationItem] = Field(
        ..., 
        description="List of similar movies"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "movie_id": 1,
                "movie_title": "Toy Story (1995)",
                "recommendations": [
                    {
                        "movie_id": 3114,
                        "title": "Toy Story 2 (1999)",
                        "genres": "Adventure|Animation|Children|Comedy|Fantasy",
                        "score": 0.95
                    },
                    {
                        "movie_id": 78499,
                        "title": "Toy Story 3 (2010)",
                        "genres": "Adventure|Animation|Children|Comedy|Fantasy",
                        "score": 0.92
                    }
                ]
            }
        }

class PersonalizedRequest(BaseModel):
    """Request for personalized recommendations"""
    user_id: Optional[int] = Field(None, description="User ID (optional)", ge=1)
    liked_movies: Optional[List[int]] = Field(
        None, 
        description="List of movie IDs user liked",
        min_items=0,
        max_items=50
    )
    genres: Optional[List[str]] = Field(
        None,
        description="Preferred genres",
        min_items=0,
        max_items=10
    )
    tags: Optional[List[str]] = Field(
        None,
        description="Preferred tags",
        min_items=0,
        max_items=20
    )
    top_n: int = Field(10, description="Number of recommendations", ge=1, le=50)
    
    @validator('liked_movies')
    def validate_liked_movies(cls, v):
        if v is not None and len(v) > 0:
            # Remove duplicates
            return list(set(v))
        return v
    
    @validator('genres')
    def validate_genres(cls, v):
        if v is not None:
            # Capitalize first letter
            return [g.capitalize() for g in v]
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 123,
                "liked_movies": [1, 260, 318],
                "genres": ["Action", "Sci-Fi"],
                "tags": ["superhero", "space"],
                "top_n": 10
            }
        }


class PersonalizedResponse(BaseModel):
    strategy: str = Field(..., description="Recommendation strategy used")
    recommendations: List[RecommendationItem] = Field(
        ...,
        description="List of personalized recommendations"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "strategy": "PERSONALIZED_CBF",
                "recommendations": [
                    {
                        "movie_id": 260,
                        "title": "Star Wars: Episode IV - A New Hope (1977)",
                        "genres": "Action|Adventure|Sci-Fi",
                        "score": 0.89
                    }
                ]
            }
        }


class MovieSearchResult(BaseModel):
    """Single search result"""
    movie_id: int = Field(..., description="Movie ID", ge=1)
    title: str = Field(..., description="Movie title")
    genres: str = Field("", description="Pipe-separated genres")
    plot: str = Field("", description="Movie plot/description")
    score: float = Field(..., description="Search relevance score", ge=0)
    
    class Config:
        json_schema_extra = {
            "example": {
                "movie_id": 260,
                "title": "Star Wars: Episode IV - A New Hope (1977)",
                "genres": "Action|Adventure|Sci-Fi",
                "plot": "Luke Skywalker joins forces with a Jedi Knight...",
                "score": 0.87
            }
        }


class GenreRecommendationResponse(BaseModel):
    """Response for genre-based recommendations"""
    strategy: str = Field(..., description="Strategy used (e.g., GENRE_ACTION_POPULARITY)")
    recommendations: List[RecommendationItem] = Field(
        ...,
        description="List of movies in the genre"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "strategy": "GENRE_ACTION_POPULARITY",
                "recommendations": [
                    {
                        "movie_id": 260,
                        "title": "Star Wars: Episode IV - A New Hope (1977)",
                        "genres": "Action|Adventure|Sci-Fi",
                        "score": 8.5
                    }
                ]
            }
        }

class TrendingResponse(BaseModel):
    """Response for trending movies"""
    strategy: str = Field(..., description="Strategy used (e.g., TRENDING_7D)")
    recommendations: List[RecommendationItem] = Field(
        ...,
        description="List of trending movies"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "strategy": "TRENDING_7D",
                "recommendations": [
                    {
                        "movie_id": 318,
                        "title": "The Shawshank Redemption (1994)",
                        "genres": "Crime|Drama",
                        "score": 450.5
                    }
                ]
            }
        }


class UserRecommendationRequest(BaseModel):
    """Request for user-based CF recommendations"""
    user_id: int = Field(..., description="User ID", ge=1)
    top_n: int = Field(10, description="Number of recommendations", ge=1, le=50)
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 123,
                "top_n": 10
            }
        }


class SimilarUsersResponse(BaseModel):
    """Response for similar users"""
    user_id: int = Field(..., description="Target user ID")
    similar_users: List[dict] = Field(
        ...,
        description="List of similar users with similarity scores"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 123,
                "similar_users": [
                    {"user_id": 456, "similarity": 0.85},
                    {"user_id": 789, "similarity": 0.78}
                ]
            }
        }


class HybridRequest(BaseModel):
    """Request for hybrid recommendations (CBF + CF)"""
    user_id: int = Field(..., description="User ID", ge=1)
    movie_id: Optional[int] = Field(None, description="Seed movie ID (optional)", ge=1)
    cf_weight: float = Field(
        0.7, 
        description="Weight for collaborative filtering (0-1)",
        ge=0,
        le=1
    )
    cbf_weight: float = Field(
        0.3,
        description="Weight for content-based filtering (0-1)",
        ge=0,
        le=1
    )
    top_n: int = Field(10, description="Number of recommendations", ge=1, le=50)
    
    @validator('cbf_weight')
    def validate_weights(cls, v, values):
        if 'cf_weight' in values:
            total = v + values['cf_weight']
            if abs(total - 1.0) > 0.01:  # Allow small floating point errors
                raise ValueError("cf_weight + cbf_weight must equal 1.0")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 123,
                "movie_id": 260,
                "cf_weight": 0.7,
                "cbf_weight": 0.3,
                "top_n": 10
            }
        }


class HybridResponse(BaseModel):
    strategy: str = Field(..., description="Strategy used (e.g., HYBRID_CF0.7_CBF0.3)")
    recommendations: List[RecommendationItem] = Field(
        ...,
        description="List of hybrid recommendations"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "strategy": "HYBRID_CF0.7_CBF0.3",
                "recommendations": [
                    {
                        "movie_id": 260,
                        "title": "Star Wars: Episode IV - A New Hope (1977)",
                        "genres": "Action|Adventure|Sci-Fi",
                        "score": 0.91
                    }
                ]
            }
        }

class ErrorResponse(BaseModel):
    """Standard error response"""
    detail: str = Field(..., description="Error message")
    
    class Config:
        json_schema_extra = {
            "example": {
                "detail": "Movie 99999 not found"
            }
        }

class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Service status (healthy/unhealthy)")
    elasticsearch: str = Field(..., description="Elasticsearch status")
    database: str = Field(..., description="Database status")
    error: Optional[str] = Field(None, description="Error message if unhealthy")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "elasticsearch": "green",
                "database": "connected"
            }
        }

class MovieMetadata(BaseModel):
    movie_id: int
    title: str
    genres: str
    tags: Optional[str] = None
    plot: Optional[str] = None
    release_date: Optional[datetime] = None
    popularity: Optional[float] = None
    avg_rating: Optional[float] = None
    rating_count: Optional[int] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "movie_id": 260,
                "title": "Star Wars: Episode IV - A New Hope (1977)",
                "genres": "Action|Adventure|Sci-Fi",
                "tags": "space, rebellion, jedi",
                "plot": "Luke Skywalker joins forces...",
                "release_date": "1977-05-25T00:00:00",
                "popularity": 8.5,
                "avg_rating": 4.2,
                "rating_count": 15234
            }
        }
