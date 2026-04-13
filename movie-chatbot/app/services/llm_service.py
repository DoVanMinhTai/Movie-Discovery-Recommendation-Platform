from groq import AsyncGroq
from app.config.config import settings
from app.config.prompts import Prompts
from app.services.helpers import clean_json_response, format_movie_summary
import os

class LLMService:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            print("Warning: GROQ_API_KEY is not set. LLM functionalities will be limited.")
        self.model_name = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

        try:
            self.client = AsyncGroq(api_key=api_key)
            print(f"Initialized LLMService with model: {self.model_name}")
        except Exception as e:
            print(f"LLM Error: {e}")
            self.client = None

    async def generate_suggestions(self, user_query: str, bot_response: str, intent: str):
        prompt = f"""
        Bạn là một chuyên gia tư vấn phim ảnh. 
        Dựa trên câu hỏi của người dùng: "{user_query}" 
        Và câu trả lời của hệ thống: "{bot_response}"
        Với mục đích (intent): "{intent}"

        Hãy đưa ra chính xác 3 câu hỏi gợi ý ngắn gọn (dưới 10 từ mỗi câu) mà người dùng có thể muốn hỏi tiếp theo.
        Yêu cầu:
        1. Trả về dưới dạng danh sách JSON: ["gợi ý 1", "gợi ý 2", "gợi ý 3"]
        2. Không giải thích gì thêm, chỉ trả về JSON.
        3. Các gợi ý phải tự nhiên, kích thích sự tò mò.
        """
        try:
            response_json = await self._call_groq_api(
                system_prompt=prompt,
                user_message="",
                temperature=0.7,
            )
            import json
            suggestions = json.loads(response_json)
            return suggestions if isinstance(suggestions, list) else []

        except Exception as e:
            print(f"Error generating suggestions: {e}")
            return []

    async def _call_groq_api(self, system_prompt: str, user_message: str, max_tokens: int = 150, temperature: float = 0.7, stop: list = None):
        if not self.client:
            return None
        try:
            completion = await self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=max_tokens,
                temperature=temperature,
            )
            return completion.choices[0].message.content.strip()
        except Exception as e:
            print(f"Groq API Error: {e}")
            return None

    def generate_natural_response(self, message: str, movies_data: list, intent: str | None = None):
        if not self.client:
            return f"Tìm thấy {len(movies_data)} phim: " + ", ".join([m.get('title') for m in movies_data])
            
        summary = format_movie_summary(movies_data)
        system_prompt = "Bạn là trợ lý ảo về phim ảnh thân thiện. Hãy dựa vào danh sách phim được cung cấp để trả lời người dùng bằng tiếng Việt tự nhiên."
        user_prompt = f"Câu hỏi của người dùng: {message}\n\nDanh sách phim: {summary}\n\nÝ định (Intent): {intent}\n\nHãy trả lời một cách lôi cuốn."
        
        return self._call_groq_api(system_prompt, user_prompt, max_tokens=1000)

    def extract_search_params(self, text: str):
        system_prompt = "Bạn là chuyên gia trích xuất thực thể từ câu lệnh tìm kiếm phim. Chỉ trả về JSON, không giải thích gì thêm."
        user_prompt = f"Trích xuất các tham số tìm kiếm (title, genre, year, actor, director) từ câu sau: '{text}'"
        
        raw_output = self._call_groq_api(system_prompt, user_prompt, max_tokens=150, temperature=0.1)
        return clean_json_response(raw_output) or {"title": text}

    def extract_reference_movie(self, text: str):
        system_prompt = "Nhiệm vụ của bạn là trích xuất duy nhất tên bộ phim mà người dùng đang nhắc tới. Nếu không thấy, hãy trả về 'None'."
        user_prompt = f"Trích xuất tên phim từ câu: '{text}'"
        
        result = self._call_groq_api(system_prompt, user_prompt, max_tokens=50, temperature=0.1)
        return None if "None" in result else result

    def handle_generic_chat(self, message: str):
        system_prompt = "Bạn là trợ lý ảo về phim ảnh thân thiện. Trả lời ngắn gọn, hóm hỉnh bằng tiếng Việt."
        return self._call_groq_api(system_prompt, message, max_tokens=500)