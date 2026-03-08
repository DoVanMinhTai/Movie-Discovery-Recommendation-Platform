import requests
from app.services.search_service import SearchService
from app.config.config import settings

class RecommendationService:
    def __init__(self) -> None:
        self.search_service = SearchService()

    def call_recommendation(self, inputs: dict):
        REC_SERVICE_URL = settings.recommendation_service_url 
        
        try:
            response = requests.post(REC_SERVICE_URL, json=inputs, timeout=10)
            if response.status_code == 200:
                return response.json() 
        except Exception as e:
            print(f"Failed to call Recommendation Service: {e}")
            
            # PM Tip: Nếu Service gợi ý sập, hãy trả về kết quả từ Elasticsearch như một phương án dự phòng (Fallback)
            return self.search_service.search_movies({"genre": inputs["selected_genres"][0] if inputs["selected_genres"] else "Action"})
        
        return []
   