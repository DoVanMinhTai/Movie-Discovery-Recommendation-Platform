from elasticsearch import Elasticsearch
from app.config.config import settings
from app.services.nlp_service import NLPService
from app.services.search_service import SearchService
from app.services.llm_service import LLMService
from app.services.helpers import extract_genres_by_regex
from app.services.recommendation_service import RecommendationService
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ChatBotService")

class ChatBotService:
    def __init__(self):
        self.nlp = NLPService()
        self.search_service = SearchService()
        self.llm_service = LLMService()
        self.es_client = Elasticsearch(settings.es_host)
        self.recommendation_service = RecommendationService()

    def _format_response(self, intent: str, message: str, data: list = None, suggestions: list = None):
        return {
            "status": "success",
            "metadata": {
                "intent": intent,
                "model": "llama-3.3-70b-versatile",
                "timestamp": logging.time.time()
            },
            "message": message,
            "data": data,
            "suggestions": suggestions
        }

    async def process_query(self, message: str, userId: int):
        logger.info(f"Starting process_query_stream for user {userId}")
        try:
            intent = self.nlp.detect_intent(message)

            if intent == "SEARCH":
                result = await self.handle_search(message)
            elif intent == "RECOMMEND":
                result = await self.handle_recommendation(message, userId, intent)
            elif intent == "CHAT":
                result = await self.handle_chat(message)
            else:
                result = {
                    "message": "Xin lỗi, tôi chưa hiểu rõ ý bạn. Bạn muốn tìm thông tin phim hay cần gợi ý phim?",
                } 

            suggestions = await self.llm_service.generate_suggestions(user_query=message, bot_response=result["message"], intent=intent)

            return self._format_response(intent, result["message"], data=result.get("data"), suggestions=suggestions)
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return self._format_response("ERROR", "Đã có lỗi xảy ra. Vui lòng thử lại sau.")

    async def handle_recommendation(self, message: str, userId: int, intent: str):
        extracted = extract_genres_by_regex(message)
        ref_movie = await self.llm_service.extract_reference_movie(message)
            
        rec_inputs = {
                "user_id": userId,
                "selected_genres": extracted,
                "current_movie_id": [],
                "limit": 5,
                "strategy": "collaborative"
        } 
            
        if ref_movie:
            movie_id = await self.search_service.find_movie_id_by_name(ref_movie)
            if movie_id:
                rec_inputs["current_movie_id"] = movie_id
                rec_inputs["strategy"] = "content_based"
            else:
                rec_inputs["current_movie_id"] = await self.search_service.fall_Back_ElasticSearch(ref_movie)
        
        rec_results = self.recommendation_service.call_recommendation(rec_inputs)
            
        msg = await self.llm_service.generate_natural_response(message, rec_results, intent)
        return {"message": msg, "data": rec_results}
    
    async def handle_chat(self, message: str):
        answer = await self.llm_service.handle_generic_chat(message)
        return {"message": answer, "data": None}
   
    async def handle_search(self, message:str): 
        params = await self.llm_service.extract_search_params(message)
        movies_data = await self.search_service.search_movies(params)
        natural_answer =  await self.llm_service.generate_natural_response(message, movies_data)
            
        return {    
            "message": natural_answer,
            "data": movies_data
        }
   
