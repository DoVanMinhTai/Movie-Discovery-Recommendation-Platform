import re
import json
from app.config.config import settings

def clean_json_response(raw_output: str) -> dict:
    try:
        clean_json = re.sub(r'```json|```', '', raw_output).strip()
        return json.loads(clean_json)
    except Exception:
        return {}

def extract_genres_by_regex(text: str) -> list:
    detected = []
    text_lower = text.lower()
    for k, v in settings.genre_map.items():
        if re.search(r'\b' + re.escape(k) + r'\b', text_lower):
            if v not in detected:
                detected.append(v)
    return detected

def format_movie_summary(movies_data: list) -> str:
    if not movies_data:
        return ""
    return "\n".join([
        f"- {m.get('title')} ({m.get('release_year', 'N/A')}) bởi {m.get('director_name', 'N/A')}" 
        for m in movies_data
    ])