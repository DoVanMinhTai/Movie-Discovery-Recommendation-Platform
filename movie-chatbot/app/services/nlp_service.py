import os
import re
import logging
from groq import Groq

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("NLPService")

class NLPService:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        self.model_name = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        self.client = Groq(api_key=api_key)

    def detect_intent(self, text: str, llm_instance=None) -> str:
        quick_intent = self._detect_via_regex(text)
        if quick_intent: return quick_intent

        system_prompt = (
            "Bạn là bộ phận phân loại ý định người dùng cho hệ thống gợi ý phim. "
            "Chỉ trả về 1 từ duy nhất trong danh sách: SEARCH, RECOMMEND, CHAT. "
            "- SEARCH: Khi người dùng muốn tìm thông tin về 1 bộ phim cụ thể, diễn viên, đạo diễn hoặc năm sản xuất. "
            "- RECOMMEND: Khi người dùng muốn được gợi ý phim theo sở thích, thể loại, hoặc tâm trạng (ví dụ: 'gợi ý cho tôi phim hay', 'nên xem phim gì'). "
            "- CHAT: Khi người dùng chào hỏi, hỏi về bạn, hoặc nói chuyện phiếm."
        )

        try:
            completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text}
                ],
                max_tokens=10,
                temperature=0.1 
            )
            response = completion.choices[0].message.content.strip().upper()
            
            for label in ["SEARCH", "RECOMMEND", "CHAT"]:
                if label in response:
                    return label
            return "CHAT" 
        except Exception as e:
            logger.error(f"Lỗi phân loại ý định: {e}")
            return "CHAT"
       
    def _detect_via_regex(self, text: str) -> str:
        patterns = {
             "CHAT": r"\b(chào|hi|hello|hey)\b",
            "SEARCH": r"\b(tìm phim|thông tin về|ai đóng vai)\b",
            "RECOMMEND": r"\b(gợi ý|đề xuất|nên xem phim gì)\b"
        }
        for intent, pattern in patterns.items():
            if re.search(pattern, text.lower()):
                return intent
        return None

# def _detect_via_embedding(self, text: str):
#         user_embedding = self.embed_model.encode(text, convert_to_tensor=True)
#         best_intent = "UNKNOWN"
#         max_score = 0.0
        
#         for intent, anchors in self.anchor_embeddings.items():
#             scores = util.cos_sim(user_embedding, anchors)
#             top_val, _ = torch.topk(scores, k=min(2, scores.shape[1]))
#             current_avg = float(torch.mean(top_val))
            
#             if current_avg > max_score:
#                 max_score = current_avg
#                 best_intent = intent
        
#         return best_intent, max_score

# def _detect_via_llm(self, text: str, llm) -> str:
#     prompt = (
#         f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n"
#         f"Bạn là bộ phận phân loại ý định người dùng. Chỉ trả ra 1 từ duy nhất: SEARCH, RECOMMEND, CHAT.\n"
#         f"SEARCH: Tìm phim/thông tin cụ thể.\n"
#         f"RECOMMEND: Xin gợi ý phim.\n"
#         f"CHAT: Chào hỏi/tán gẫu.<|eot_id|>"
#         f"<|start_header_id|>user<|end_header_id|>\n\n"
#         f"Câu: '{text}'\n"
#         f"Intent:<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"
#     )
    
#     try:
#         output = llm(prompt, max_tokens=10, stop=["<|eot_id|>"])
#         response = output['choices'][0]['text'].strip().upper()
        
#         for label in ["SEARCH", "RECOMMEND", "CHAT"]:
#             if label in response:
#                 print(f"[Intent] Tầng 3 (LLM) xác định: {label}")
#                 return label
#         logger.warning(f"[Tầng 3 - LLM] LLM trả về kết quả lạ: {response}. Default: CHAT")
#         return "CHAT"
#     except Exception as e:
#         print(f"Lỗi Tầng 3: {e}")
#         return "CHAT"