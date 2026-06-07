import os
import logging
from typing import Optional, List, Dict
from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_classic.agents import create_openai_tools_agent, AgentExecutor
from app.services.search_service import SearchService
from app.services.recommendation_service import RecommendationService
import time

logger = logging.getLogger("NLPService")

class NLPService:
    def __init__(self):
        self.search_service = SearchService()
        self.rec_service = RecommendationService()
        
        api_key = os.getenv("GROQ_API_KEY")
        self.llm = ChatGroq(groq_api_key=api_key, model_name="llama-3.3-70b-versatile", temperature=0.1)

        self.tools = self._setup_tools()
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", (
                "Bạn là trợ lý điện ảnh. "
                "1. Để tìm kiếm: dùng 'search_movies'. "
                "2. Để gợi ý cá nhân: dùng 'get_user_recommendations'. "
                "3. Để tìm phim tương tự: dùng 'get_similar_movies'. "
                "Nếu không có dữ liệu gợi ý, hãy chủ động tìm phim hot để đề xuất cho khách."
            )),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        agent = create_openai_tools_agent(self.llm, self.tools, self.prompt)
        self.agent_executor = AgentExecutor(
            agent=agent, 
            tools=self.tools, 
            verbose=True, 
            handle_parsing_errors=True,
            return_intermediate_steps=True
        )

    def _format_response(self, intent: str, message: str, movies: any = None, suggestions: list = None):
        return {
            "status": "success",
            "metadata": {
                "intent": intent,
                "model": "llama-3.3-70b-versatile",
                "timestamp": time.time()
            },
            "message": message,
            "movies": movies,
            "suggestions": suggestions
        }

    def _setup_tools(self):
        @tool("search_movies")
        async def search_movies(query: str) -> str:
            """Tìm kiếm phim trong hệ thống."""
            res = await self.search_service.search_movies(query)
            return str(res) if res else "Không tìm thấy phim nào."

        @tool("get_user_recommendations")
        async def get_user_recommendations(user_id: int) -> str:
            """Lấy danh sách phim gợi ý cho một ID người dùng nhất định."""
            if user_id <= 0:
                return "User mới, chưa có lịch sử. Hãy gợi ý phim phổ biến thay thế."
            res = await self.rec_service.get_hybrid_recommendations(user_id)
            return str(res) if res else "Không có dữ liệu gợi ý."

        @tool("get_similar_movies")
        async def get_similar_movies(movie_name: str) -> str:
            """Tìm phim tương tự phim mà người dùng nhắc tới."""
            movie_id = await self.search_service.find_movie_id_by_name(movie_name)
            if movie_id:
                res = await self.rec_service.get_similar_movies(movie_id)
                return str(res)
            return "Không tìm thấy phim tương tự."

        return [search_movies, get_user_recommendations, get_similar_movies]

    async def process_message(self, user_input: str, user_id: int, chat_history: List = []):
        try:
            context_input = f"[User_ID: {user_id}] {user_input}"
            result = await self.agent_executor.ainvoke({
                "input": context_input,
                "chat_history": chat_history
            })

            final_answer = result.get("output")

            raw_data = None
            steps = result.get("intermediate_steps", [])
            
            if steps:
                last_step_output = steps[-1][1] 
                raw_data = last_step_output

            return self._format_response("AUTO", final_answer, movies=raw_data)
        except Exception as e:
            logger.error(f"Agent execution error: {e}")
            return "Chào bạn, tôi chưa rõ ý của bạn lắm. Bạn muốn tìm phim hay nhận gợi ý?"
