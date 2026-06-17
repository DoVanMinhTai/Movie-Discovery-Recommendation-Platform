from fastapi import APIRouter, HTTPException, BackgroundTasks
import os
import redis
from elasticsearch import Elasticsearch

from ..services.redis_cache_service import RedisCacheService
from ..services.similarity_precompute_service import SimilarityPrecomputeService

router = APIRouter(prefix="/api/recommendations", tags=["recommendations"])

ES_URL = os.getenv('ES_URL', 'http://localhost:9200')
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')

es_client = Elasticsearch([ES_URL])
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

cache_service = RedisCacheService(REDIS_URL)
precompute_service = SimilarityPrecomputeService(es_client, redis_client, top_k=int(os.getenv('SIM_TOPK', 50)))


@router.get('/similar/{movie_id}')
def get_similar_movies(movie_id: str, top_k: int = 10, use_cache: bool = True):
    """Return top-K similar movies for a movie. Uses Redis cache if available."""
    try:
        if use_cache:
            cached = cache_service.get_similar_movies(movie_id, top_k)
            if cached:
                return {
                    'movie_id': movie_id,
                    'similar_movies': cached,
                    'source': 'cache',
                    'cached': True
                }

        # Cache miss or disabled: compute via ES
        sims = precompute_service.compute_similarities_for_movie(movie_id, vectors_index=os.getenv('VECTORS_INDEX', 'movies_vectors'))
        if sims:
            cache_service.cache_similar_movies(movie_id, sims, top_k)
        return {
            'movie_id': movie_id,
            'similar_movies': sims[:top_k],
            'source': 'elasticsearch',
            'cached': False
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/precompute')
def trigger_precompute(background_tasks: BackgroundTasks, batch_size: int = 50):
    """Trigger precomputation job for popular movies (runs in background)."""
    try:
        background_tasks.add_task(precompute_service.precompute_all, batch_size)
        return {'status': 'scheduled', 'batch_size': batch_size}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/cache/stats')
def cache_stats():
    try:
        stats = cache_service.get_cache_stats()
        total = int(stats.get('hit', 0)) + int(stats.get('miss', 0))
        hit_rate = (int(stats.get('hit', 0)) / total) if total > 0 else 0.0
        return {
            'stats': stats,
            'total_requests': total,
            'cache_hits': int(stats.get('hit', 0)),
            'cache_misses': int(stats.get('miss', 0)),
            'hit_rate': f"{hit_rate:.2%}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
