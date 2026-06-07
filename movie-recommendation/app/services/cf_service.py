from typing import List, Any, Optional, Dict
import logging
from opensearchpy import OpenSearch
from app.schemas.recommendation import (
    PersonalizedResponse,
    RecommendationItem
)

logger = logging.getLogger("CollaborativeService")

class CollaborativeService:
    def __init__(self, es_client: OpenSearch):
        self.es = es_client
        self.index_name = "movies_cf"

    async def get_user_recommendations(self, user_id: int, top_n: int = 10) -> List[RecommendationItem]:
        """
        Gợi ý phim cho người dùng bằng cách lấy trung bình vector các phim họ đã thích 
        rồi tìm kiếm Vector tương đồng trong ES.
        """
        try:
            info = self.es.info()
            logger.info(f"Đang kết nối tới Cluster: {info['cluster_name']} tại {self.es.transport.hosts}")
            logger.info(f"Đang tìm kiếm user_id: {user_id} kiểu {type(user_id)}")
            print(f"Đang tìm kiếm user_id: {user_id} kiểu {type(user_id)}")
            print(f"{self.es.transport.hosts}")
            print(f"Cluster info: {info}")

            user_res = self.es.get(index="user_vectors", id=str(user_id))
            user_vector = user_res['_source']['user_vector']

            query = {
                "size": top_n,
                "query": {
                    "knn": {
                        "movie_vector": {
                            "vector": user_vector,
                            "k": top_n
                        }
                    }
                }
            }

            response = self.es.search(index="movie_vectors", body=query)
            hits = response['hits']['hits']

            return [
                RecommendationItem(
                    movie_id=int(hit['_source']['movieId']),
                    score=float(hit['_score'])
                ) for hit in hits
            ]
        except Exception as e:
            logger.error(f"Error in User Vector Search: {e}")
            return []

    async def get_item_based_similar(self, movie_id: int, top_n: int = 10) -> List[RecommendationItem]:
        """
        Tìm kiếm các phim tương đồng với movie_id bằng KNN Vector Search.
        """
        try:
            source_movie = self.es.get(index=self.index_name, id=str(movie_id))
            query_vector = source_movie['_source']['movie_vector']

            query = {
                "size": top_n + 1,
                "query": {
                    "knn": {
                        "movie_vector": {
                            "vector": query_vector,
                            "k": top_n + 1
                        }
                    }
                }
            }

            response = self.es.search(index=self.index_name, body=query)
            hits = response['hits']['hits']

            recommendations = []
            for hit in hits:
                target_id = int(hit['_id'])
                if target_id == movie_id:
                    continue 
                
                recommendations.append(RecommendationItem(
                    movie_id=target_id,
                    score=float(hit['_score'])
                ))
            
            return recommendations[:top_n]

        except Exception as e:
            logger.error(f"Error in Item Vector Search for movie {movie_id}: {e}")
            return []