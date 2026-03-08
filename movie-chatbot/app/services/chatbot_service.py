from click import prompt
from sqlalchemy import text
from elasticsearch import Elasticsearch
from gpt4all import GPT4All
from underthesea import pos_tag
from app.config.config import settings
from app.services.nlp_service import NLPService
from app.services.search_service import SearchService
from app.services.llm_service import LLMService
from app.services.helpers import extract_genres_by_regex
from app.services.recommendation_service import RecommendationService

class ChatBotService:
    def __init__(self):
        self.nlp = NLPService()
        self.search_service = SearchService()
        self.llm_service = LLMService()
        self.es_client = Elasticsearch(settings.es_host)
        self.recommendation_service = RecommendationService()

               
    async def process_query_stream(self, message: str, userId: int):
        intent = self.nlp.detect_intent(message)
        
        if intent == "SEARCH":
            search_params = self.llm_service.extract_search_params(message)
            movies_data = self.search_service.search_movies(search_params)
            natural_answer = self.llm_service.generate_natural_response(message, movies_data)
            
            yield {"intent": "SEARCH", "message": natural_answer, "data": movies_data}
        
        elif intent == "RECOMMEND":
            rec_result = self.handle_recommendation(message, userId)
            yield rec_result
            
        elif intent == "CHAT":
            chat_result = self.handle_chat(message)
            yield {"intent": "CHAT", **chat_result}
            
        else:
            yield {
                "intent": "UNKNOWN",
                "message": "Xin lỗi, tôi chưa hiểu rõ ý bạn. Bạn muốn tìm thông tin phim hay cần gợi ý phim?",
                "data": None
            } 

    def handle_recommendation(self, message: str, userId: int):
        extracted = extract_genres_by_regex(message)
        ref_movie = self.llm_service.extract_reference_movie(message)
            
        rec_inputs = {
                "user_id": userId,
                "selected_genres": extracted,
                "current_movie_id": [],
                "limit": 5,
                "strategy": "collaborative"
        } 
            
        if ref_movie:
            movie_id = self.search_service.find_movie_id_by_name(ref_movie)
            if movie_id:
                rec_inputs["current_movie_id"] = movie_id
                rec_inputs["strategy"] = "content_based"
            else:
                rec_inputs["current_movie_id"] = self.search_service.fall_Back_ElasticSearch(ref_movie)
        
        rec_results = self.recommendation_service.call_recommendation(rec_inputs)
            
        msg = self.llm_service.generate_natural_response(message, rec_results)
        return {"intent": "RECOMMEND", "message": msg, "data": rec_results}
    
    def handle_chat(self, message: str):
        answer = self.llm_service.handle_generic_chat(message)
        return {"message": answer, "data": None}
   
    def handle_search(self, message:str): 
        params = self.llm_service.extract_search_params(message)
        movies_data = self.search_service.search_movies(params)
        natural_answer = self.llm_service.generate_natural_response(message, movies_data)
            
        return {
            "intent": "SEARCH",
            "message": natural_answer,
            "data": movies_data
        }
   
