class Prompts:
    @staticmethod
    def get_search_param_prompt(text: str) -> str:
        return f"""[INST] Trích xuất các tham số tìm kiếm từ câu sau dưới dạng JSON.
    Các trường: title, director, genre, year.
    Câu: "{text}"
    Chỉ trả về JSON, không giải thích. [/INST]"""

    @staticmethod
    def get_natural_answer_prompt(message: str, summary: str) -> str:
        return f"""[INST] Dựa vào danh sách phim sau, hãy trả lời câu hỏi của người dùng một cách thân thiện.
    Danh sách:
    {summary}
    Câu hỏi: "{message}" [/INST]"""
    
    @staticmethod
    def get_recommend_extract_prompt(text: str) -> str:
        return f"""[INST] Trích xuất tên bộ phim từ câu sau. Chỉ trả về duy nhất tên phim.
    Câu: "{text}" -> Output: [/INST]"""