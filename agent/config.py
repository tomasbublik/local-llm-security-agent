from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseModel):
    ollama_model: str = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:14b")
    ollama_host: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

settings = Settings()
