import torch
from sentence_transformers import SentenceTransformer, util
from app.config.config import settings
import re

class NLPService:
    def __init__(self):
        self.embed_model = SentenceTransformer(settings.embed_model_name, cache_folder=settings.model_path)
        self.anchor_embeddings = {
            intent: self.embed_model.encode(anchors, convert_to_tensor=True) 
            for intent, anchors in settings.intent_anchors.items()
        }

        self.quick_patterns = {
            "CHAT": r"^(chào|hi|hello|tạm biệt|bye|cảm ơn|thanks|bạn là ai|hey)",
            "SEARCH": r"^(tìm|search|kiếm|cho xem|thông tin phim)",
            "RECOMMEND": r"^(gợi ý|đề xuất|nên xem gì|tư vấn|phim nào hay)"
        }

    def detect_intent(self, text: str, llm_instance=None) -> str:

        intent = self._detect_via_regex(text)
        if intent:
            return intent

        intent, score = self._detect_via_embedding(text)

        if score > 0.6:
            return intent

        if llm_instance:
            return self._detect_via_llm(text, llm_instance)
                
        return intent if score > 0.4 else "UNKNOWN"
       
    def _detect_via_regex(self, text: str) -> str:
            for intent, pattern in self.quick_patterns.items():
                if re.search(pattern, text):
                    return intent
            return None

    def _detect_via_embedding(self, text: str):
            user_embedding = self.embed_model.encode(text, convert_to_tensor=True)
            best_intent = "UNKNOWN"
            max_score = 0.0
            
            for intent, anchors in self.anchor_embeddings.items():
                scores = util.cos_sim(user_embedding, anchors)
                top_val, _ = torch.topk(scores, k=min(2, scores.shape[1]))
                current_avg = float(torch.mean(top_val))
                
                if current_avg > max_score:
                    max_score = current_avg
                    best_intent = intent
            
            return best_intent, max_score

    def _detect_via_llm(self, text: str, llm) -> str:
        prompt = (
            f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n"
            f"Bạn là bộ phận phân loại ý định người dùng. Chỉ trả ra 1 từ duy nhất: SEARCH, RECOMMEND, CHAT.\n"
            f"SEARCH: Tìm phim/thông tin cụ thể.\n"
            f"RECOMMEND: Xin gợi ý phim.\n"
            f"CHAT: Chào hỏi/tán gẫu.<|eot_id|>"
            f"<|start_header_id|>user<|end_header_id|>\n\n"
            f"Câu: '{text}'\n"
            f"Intent:<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"
        )
        
        try:
            output = llm(prompt, max_tokens=10, stop=["<|eot_id|>"])
            response = output['choices'][0]['text'].strip().upper()
            
            for label in ["SEARCH", "RECOMMEND", "CHAT"]:
                if label in response:
                    print(f"[Intent] Tầng 3 (LLM) xác định: {label}")
                    return label
            return "CHAT"
        except Exception as e:
            print(f"Lỗi Tầng 3: {e}")
            return "CHAT"