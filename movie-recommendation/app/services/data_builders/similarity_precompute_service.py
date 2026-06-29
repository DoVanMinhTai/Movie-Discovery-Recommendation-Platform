import json
import logging
from typing import List, Tuple, Dict
from elasticsearch import Elasticsearch
from redis import Redis
from tqdm import tqdm


class SimilarityPrecomputeService:
    """Precompute top-K similar items using ES vector search and cache results in Redis."""

    def __init__(self, es_client: Elasticsearch, redis_client: Redis, top_k: int = 50, popularity_threshold: int = 100):
        self.es = es_client
        self.redis = redis_client
        self.top_k = top_k
        self.popularity_threshold = popularity_threshold
        self.logger = logging.getLogger(__name__)

    def get_popular_movies(self, index: str = 'movies_metadata', size: int = 1000) -> List[Tuple[str, float]]:
        """Return list of popular movie ids with a popularity metric."""
        agg_query = {
            "size": 0,
            "aggs": {
                "popular_movies": {
                    "terms": {
                        "field": "movie_id",
                        "size": size,
                        "order": {"total_clicks": "desc"}
                    },
                    "aggs": {
                        "total_clicks": {"sum": {"field": "interaction_count"}}
                    }
                }
            }
        }
        res = self.es.search(index=index, body=agg_query)
        buckets = res.get('aggregations', {}).get('popular_movies', {}).get('buckets', [])
        popular = []
        for b in buckets:
            clicks = b.get('total_clicks', {}).get('value', 0)
            if clicks >= self.popularity_threshold:
                popular.append((b.get('key'), float(clicks)))
        self.logger.info('Found %d popular movies', len(popular))
        return popular

    def compute_similarities_for_movie(self, movie_id: str, vectors_index: str = 'movies_vectors') -> List[Dict]:
        """Compute top-K similar movies for a single movie using ES vector search."""
        try:
            doc = self.es.get(index=vectors_index, id=movie_id)
        except Exception as e:
            self.logger.debug('Movie %s not found in %s: %s', movie_id, vectors_index, e)
            return []

        vector = doc.get('_source', {}).get('vector')
        if not vector:
            return []

        query = {
            "size": self.top_k + 1,
            "_source": ["id", "title"],
            "query": {
                "script_score": {
                    "query": {"match_all": {}},
                    "script": {
                        "source": "cosineSimilarity(params.query_vector, 'vector') + 1.0",
                        "params": {"query_vector": vector}
                    }
                }
            }
        }
        res = self.es.search(index=vectors_index, body=query)
        hits = res.get('hits', {}).get('hits', [])
        similar = []
        for h in hits:
            hid = h.get('_id')
            if hid == movie_id:
                continue
            src = h.get('_source', {})
            similar.append({
                'movie_id': hid,
                'title': src.get('title'),
                'score': float(h.get('_score', 0.0))
            })
            if len(similar) >= self.top_k:
                break
        return similar

    def _cache_similarities(self, cache_key: str, similarities: List[Dict], ttl: int = 86400):
        try:
            self.redis.setex(cache_key, ttl, json.dumps(similarities))
        except Exception as e:
            self.logger.exception('Failed to cache %s: %s', cache_key, e)

    def precompute_all(self, batch_size: int = 50, metadata_index: str = 'movies_metadata', vectors_index: str = 'movies_vectors'):
        """Precompute similarities for popular movies and cache them in Redis."""
        popular = self.get_popular_movies(index=metadata_index)
        for i in range(0, len(popular), batch_size):
            batch = popular[i:i+batch_size]
            for movie_id, pop in batch:
                sims = self.compute_similarities_for_movie(movie_id, vectors_index=vectors_index)
                if sims:
                    cache_key = f'sim:movie:{movie_id}:top{self.top_k}'
                    self._cache_similarities(cache_key, sims)
        self.logger.info('Precomputation finished for %d movies', len(popular))


if __name__ == '__main__':
    import argparse
    from elasticsearch import Elasticsearch
    import redis
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument('--es', default='http://localhost:9200')
    parser.add_argument('--redis', default='redis://localhost:6379')
    parser.add_argument('--topk', type=int, default=50)
    parser.add_argument('--pop-threshold', type=int, default=100)
    parser.add_argument('--batch', type=int, default=50)
    args = parser.parse_args()

    es = Elasticsearch([args.es])
    r = redis.from_url(args.redis, decode_responses=True)
    svc = SimilarityPrecomputeService(es, r, top_k=args.topk, popularity_threshold=args.pop_threshold)
    svc.precompute_all(batch_size=args.batch)
