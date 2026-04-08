from llama_cpp import Llama
from app.config.config import settings
from app.config.prompts import Prompts
from app.services.helpers import clean_json_response, format_movie_summary
import os

class LLMService:
    def __init__(self):
        repo_id = settings.repo_id
        model_file = settings.llm_model_name

        try:
            self.model = Llama.from_pretrained(
                repo_id=repo_id,
                filename=model_file,
                n_ctx=2048,
                n_threads=4,
                n_gpu_layers=0,
                use_mlock=True,
                use_mmap=True,
            )
            print("LLM Loaded successfully.")
        except Exception as e:
            print(f"LLM Error: {e}")
            self.model = None

    def generate_natural_response(self, message: str, movies_data: list, intent: str):
        if not self.model:
            return f"Tìm thấy {len(movies_data)} phim: " + ", ".join([m.get('title') for m in movies_data])
            
        summary = format_movie_summary(movies_data)
        prompt = Prompts.get_natural_answer_prompt(message, summary, intent)
        
        try:
            response = self.model(prompt, max_tokens=200, stop=["<|eot_id|>", "User:"])
            
            answer = response['choices'][0]['text'].strip()
            return answer
        except:
            return f"Kết quả: {summary}"

    def extract_search_params(self, text: str):
        if not self.model: return {"title": text}
        
        prompt = Prompts.get_search_param_prompt(text)
        try:
            response = self.model(prompt, max_tokens=100)
            raw_output = response['choices'][0]['text'].strip()
            return clean_json_response(raw_output) or {"title": text}
        except:
            return {"title": text}

    def extract_reference_movie(self, text: str):
        if not self.model: return None
        
        prompt = Prompts.get_recommend_extract_prompt(text)
        return self._get_text_from_model(prompt, max_tokens=30)

    def handle_generic_chat(self, message: str):
        if not self.model: return "Xin chào! Tôi có thể giúp gì cho bạn?"
        
        prompt = (
            f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n"
            f"Bạn là trợ lý ảo về phim ảnh thân thiện. Trả lời ngắn gọn bằng tiếng Việt.<|eot_id|>"
            f"<|start_header_id|>user<|end_header_id|>\n\n"
            f"{message}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"
        )        
        stop = ["<|eot_id|>", "<|start_header_id|>", "User:", "Assistant:"]
        return self._get_text_from_model(prompt, max_tokens=200, stop=stop)

    def _get_text_from_model(self, prompt: str, max_tokens: int = 150, stop: list = None):
        if not self.model:
            return ""
        try:
            response = self.model(prompt, max_tokens=max_tokens, stop=stop)
            return response['choices'][0]['text'].strip()
        except Exception as e:
            print(f"Model Inference Error: {e}")
            return ""
