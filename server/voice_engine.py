import base64
import httpx
from typing import Dict, Any, Optional
from server.config import settings
from server.sentry_tracing import AgentSpan

async def synthesize_voice(text: str) -> Dict[str, Any]:
    """Synthesizes empathetic speech via ElevenLabs, with Web Speech fallback."""
    if not text:
        return {"status": "error", "message": "No text provided for speech"}

    with AgentSpan(
        operation_name="ai.agent.tts",
        description="ElevenLabs Empathetic Speech Synthesis",
        tags={"tts.provider": "elevenlabs", "voice.id": settings.elevenlabs_voice_id}
    ) as span:
        if settings.elevenlabs_api_key:
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{settings.elevenlabs_voice_id}"
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": settings.elevenlabs_api_key
            }
            payload = {
                "text": text,
                "model_id": settings.elevenlabs_model_id,
                "voice_settings": {
                    "stability": 0.65,
                    "similarity_boost": 0.8,
                    "style": 0.15,
                    "use_speaker_boost": True
                }
            }

            try:
                async with httpx.AsyncClient(timeout=20.0) as client:
                    resp = await client.post(url, headers=headers, json=payload)
                    if resp.status_code == 200:
                        audio_bytes = resp.content
                        audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
                        span.set_data("audio_size_bytes", len(audio_bytes))
                        return {
                            "status": "success",
                            "provider": "ElevenLabs Turbo v2.5",
                            "voice_id": settings.elevenlabs_voice_id,
                            "audio_b64": audio_b64,
                            "mime_type": "audio/mpeg",
                            "direct_text": text
                        }
                    else:
                        print(f"[ElevenLabs] API returned {resp.status_code}: {resp.text}")
            except Exception as e:
                print(f"[ElevenLabs] request failed: {e}")

        # Fallback to browser Web Speech API guidance
        span.set_data("fallback_mode", "web_speech_api")
        return {
            "status": "browser_fallback",
            "provider": "Browser Web Speech API (Local Fallback)",
            "voice_name": "Calm Neutral",
            "audio_b64": None,
            "mime_type": None,
            "direct_text": text
        }
