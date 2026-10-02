import os
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseModel):
    # App Settings
    app_name: str = "BugWhisperer"
    version: str = "1.0.0"
    port: int = int(os.getenv("PORT", "8000"))
    environment: str = os.getenv("ENVIRONMENT", "development")

    # Gemma (Open-Weight Model) Settings
    gemma_provider: str = os.getenv("GEMMA_PROVIDER", "auto")  # groq, huggingface, ollama, mock
    gemma_model: str = os.getenv("GEMMA_MODEL", "gemma2-9b-it")
    groq_api_key: str = os.getenv("GROQ_API_KEY", os.getenv("GEMMA_API_KEY", ""))
    huggingface_api_key: str = os.getenv("HUGGINGFACE_API_KEY", "")
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

    # ElevenLabs Settings
    elevenlabs_api_key: str = os.getenv("ELEVENLABS_API_KEY", "")
    elevenlabs_voice_id: str = os.getenv("ELEVENLABS_VOICE_ID", "EXAVITQu4vr4xnSDxMaL") # Calm, empathetic female voice (Bella) or Charlie
    elevenlabs_model_id: str = os.getenv("ELEVENLABS_MODEL_ID", "eleven_turbo_v2_5")

    # Sentry Agent Tracing
    sentry_dsn: str = os.getenv("SENTRY_DSN", "")

settings = Settings()
