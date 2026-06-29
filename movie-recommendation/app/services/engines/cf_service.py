from app.core.constants import QueryTemplates
import logging
from typing import List
from elasticsearch import AsyncElasticsearch, NotFoundError
from app.schemas.recommendation import RecommendationItem

logger = logging.getLogger("CollaborativeService")


class CollaborativeService:
    def __init__(self, es_client: AsyncElasticsearch):
        self.es = es_client
        # Tập trung hóa tên các index để dễ bảo trì
        self.item_index = "movies_cf"
        self.user_vector_index = "user_vectors"
        self.movie_vector_index = "movie_vectors"

    async def get_user_recommendations(self, user_id: int, top_n: int = 10) -> List[RecommendationItem]:
        """
        Gợi ý phim cho người dùng dựa trên User Vector đã tính toán trước (Collaborative Filtering)
        bằng KNN Vector Search trên Elasticsearch.
        """
        try:
            # Lấy vector đại diện của người dùng (Bất đồng bộ)
            try:
                user_res = await self.es.get(index=self.user_vector_index, id=str(user_id))
                user_vector = user_res['_source']['user_vector']
            except NotFoundError:
                logger.warning(f"User vector not found for user_id: {user_id}")
                return []

            # Cấu trúc câu truy vấn KNN chuẩn của Elasticsearch 8.x
            query_body = {
                "size": top_n,
                "knn": {
                    "field": "movie_vector",
                    "query_vector": user_vector,
                    "k": top_n,
                    "num_candidates": top_n * 10  # Tăng độ chính xác cho thuật toán xấp xỉ HNSW
                }
            }

            response = await self.es.search(index=self.movie_vector_index, **query_body)
            hits = response['hits']['hits']

            return [
                RecommendationItem(
                    movie_id=int(hit['_source']['movieId']),
                    score=float(hit['_score'])
                ) for hit in hits
            ]
        except Exception as e:
            logger.error(f"Error in User Vector Search for user {user_id}: {e}")
            return []

    async def get_item_based_similar(self, movie_id: int, top_n: int = 10) -> List[RecommendationItem]:
        """
        Tìm kiếm các phim tương đồng với movie_id dựa trên Item Vector (Collaborative Filtering).
        """
        try:
            # Lấy vector của bộ phim gốc
            try:
                source_movie = await self.es.get(index=self.item_index, id=str(movie_id))
                query_vector = source_movie['_source']['movie_vector']
            except NotFoundError:
                logger.warning(f"Movie vector not found for movie_id: {movie_id}")
                return []

            query_body = QueryTemplates.knn_search(
                vector=query_vector, 
                k=top_n + 1, 
                size=top_n + 1, 
                source_fields=["movieId"]
            )

            response = await self.es.search(index=self.item_index, **query_body)
            hits = response['hits']['hits']

            recommendations = []
            for hit in hits:
                # Ưu tiên lấy từ trường dữ liệu bên trong _source, nếu không có mới dùng _id làm fallback
                source = hit['_source']
                target_id = int(source.get('movieId', hit['_id']))
                
                # Loại bỏ chính bộ phim đang xem ra khỏi danh sách gợi ý tương đồng
                if target_id == movie_id:
                    continue 
                
                recommendations.append(
                    RecommendationItem(
                        movie_id=target_id,
                        score=float(hit['_score'])
                    )
                )
            
            return recommendations[:top_n]

        except Exception as e:
            logger.error(f"Error in Item Vector Search for movie {movie_id}: {e}")
            return []