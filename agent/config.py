from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseModel):
    ollama_model: str = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:14b")
    ollama_host: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    github_mode: str = os.getenv("GITHUB_MODE", "pr_only")

    target_scope: str = os.getenv("TARGET_SCOPE", "single_repo")
    target_owner: str = os.getenv("TARGET_OWNER", "")
    target_repo: str = os.getenv("TARGET_REPO", "")

    agent_workdir: str = os.getenv("AGENT_WORKDIR", "/tmp/llm-security-agent")

settings = Settings()
