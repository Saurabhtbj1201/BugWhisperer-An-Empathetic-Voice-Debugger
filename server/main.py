import os
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from server.config import settings
from server.sentry_tracing import init_sentry
from server.parser import sanitize_logs
from server.gemma_engine import analyze_with_gemma
from server.voice_engine import synthesize_voice

# Initialize Sentry with agent tracing
init_sentry()

app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="Empathetic, voice-driven rubber-duck debugger powered by Gemma 2 & ElevenLabs"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class DebugRequest(BaseModel):
    error_log: str
    code_context: Optional[str] = None
    with_voice: bool = True

class VoiceRequest(BaseModel):
    text: str

@app.get("/api/health")
async def health_check():
    """Returns application status, model configuration, and integration flags."""
    return {
        "status": "online",
        "app": settings.app_name,
        "version": settings.version,
        "gemma_model": settings.gemma_model,
        "integrations": {
            "gemma": "configured" if settings.groq_api_key else "local/fallback",
            "elevenlabs": "configured" if settings.elevenlabs_api_key else "browser_speech_fallback",
            "sentry": "active" if settings.sentry_dsn else "local_telemetry"
        }
    }

@app.post("/api/debug")
async def debug_endpoint(req: DebugRequest):
    """Processes stack trace or error log, executes Gemma 2 diagnosis, and prepares voice speech."""
    if not req.error_log or not req.error_log.strip():
        raise HTTPException(status_code=400, detail="Error log cannot be empty.")

    # 1. Privacy sanitation (strip private user paths & ANSI sequences)
    sanitized_log = sanitize_logs(req.error_log)

    # 2. Gemma 2 reasoning with ADHD cognitive pacing
    diagnosis = await analyze_with_gemma(sanitized_log, req.code_context)

    # 3. Voice generation (ElevenLabs)
    voice_data = None
    if req.with_voice and "spoken_script" in diagnosis:
        voice_data = await synthesize_voice(diagnosis["spoken_script"])

    return {
        "success": True,
        "diagnosis": diagnosis,
        "voice": voice_data,
        "sanitized_preview": sanitized_log[:200] + ("..." if len(sanitized_log) > 200 else "")
    }

@app.post("/api/voice")
async def voice_endpoint(req: VoiceRequest):
    """Generates audio for custom text or simplified explanations."""
    if not req.text or not req.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty.")
    result = await synthesize_voice(req.text)
    return result

# Mount static directory for frontend
static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static")
if os.path.exists(static_dir):
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server.main:app", host="0.0.0.0", port=settings.port, reload=True)
