from openai import OpenAI
from app.database import settings
from typing import Optional

_client: Optional[OpenAI] = None

def get_openai_client() -> OpenAI:
    global _client
    if _client is None:
        if not settings.OPENAI_API_KEY:
            raise ValueError("OpenAI API key not configured")
        _client = OpenAI(api_key=settings.OPENAI_API_KEY)
    return _client
