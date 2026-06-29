import json
import logging
from typing import List, Dict, Optional
import redis


class RedisCacheService:
    """Simple Redis cache manager for similarity lists and basic stats."""

    def __init__(self, redis_url: str = 'redis://localhost:6379'):
        self.redis = redis.from_url(redis_url, decode_responses=True)
        self.logger = logging.getLogger(__name__)
        self.PREFIX_MOVIE_SIM = 'sim:movie'
        self.PREFIX_USER_SIM = 'sim:user'
        self.STATS_KEY = 'sim:stats'

    def get_similar_movies(self, movie_id: str, top_k: int = 10) -> Optional[List[Dict]]:
        key = f"{self.PREFIX_MOVIE_SIM}:{movie_id}:top{top_k}"
        try:
            val = self.redis.get(key)
            if val:
                self._incr_stat('hit')
                return json.loads(val)
            self._incr_stat('miss')
            return None
        except Exception as e:
            self.logger.exception('Redis get error: %s', e)
            return None

    def cache_similar_movies(self, movie_id: str, similarities: List[Dict], top_k: int = 10, ttl: int = 86400):
        key = f"{self.PREFIX_MOVIE_SIM}:{movie_id}:top{top_k}"
        try:
            self.redis.setex(key, ttl, json.dumps(similarities[:top_k]))
        except Exception as e:
            self.logger.exception('Redis set error: %s', e)

    def invalidate_movie_cache(self, movie_id_pattern: str):
        try:
            keys = self.redis.keys(f"{self.PREFIX_MOVIE_SIM}:{movie_id_pattern}*")
            if keys:
                self.redis.delete(*keys)
                self.logger.info('Invalidated %d keys', len(keys))
        except Exception as e:
            self.logger.exception('Redis invalidate error: %s', e)

    def get_cache_stats(self) -> Dict:
        try:
            return self.redis.hgetall(self.STATS_KEY) or {}
        except Exception:
            return {}

    def _incr_stat(self, stat: str):
        try:
            self.redis.hincrby(self.STATS_KEY, stat, 1)
        except Exception:
            pass


if __name__ == '__main__':
    import argparse
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser()
    parser.add_argument('--redis', default='redis://localhost:6379')
    args = parser.parse_args()

    svc = RedisCacheService(args.redis)
    print('Cache stats:', svc.get_cache_stats())
