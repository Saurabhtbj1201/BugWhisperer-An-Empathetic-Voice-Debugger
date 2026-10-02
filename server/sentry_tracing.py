import time
from typing import Optional, Dict, Any
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from server.config import settings

def init_sentry():
    """Initializes Sentry SDK with performance monitoring and agent tracing."""
    if settings.sentry_dsn:
        sentry_sdk.init(
            dsn=settings.sentry_dsn,
            environment=settings.environment,
            traces_sample_rate=1.0,
            profiles_sample_rate=1.0,
            integrations=[FastApiIntegration()],
            send_default_pii=False,
            _experiments={
                "ai_agent_monitoring": True,
            }
        )
        print("[Sentry] Agent Tracing initialized successfully.")
    else:
        print("[Sentry] SENTRY_DSN not provided; running in local telemetry logging mode.")

class AgentSpan:
    """Telemetry context manager for LLM and Voice Agent operations."""
    def __init__(self, operation_name: str, description: str, tags: Optional[Dict[str, Any]] = None):
        self.operation_name = operation_name
        self.description = description
        self.tags = tags or {}
        self.span = None
        self.start_time = 0.0
        self.duration_ms = 0.0

    def __enter__(self):
        self.start_time = time.time()
        if settings.sentry_dsn:
            self.span = sentry_sdk.start_span(op=self.operation_name, description=self.description)
            for k, v in self.tags.items():
                self.span.set_tag(k, v)
            self.span.__enter__()
        return self

    def set_data(self, key: str, value: Any):
        if self.span:
            self.span.set_data(key, value)

    def record_tokens(self, prompt_tokens: int, completion_tokens: int):
        total = prompt_tokens + completion_tokens
        if self.span:
            self.span.set_data("ai.prompt_tokens", prompt_tokens)
            self.span.set_data("ai.completion_tokens", completion_tokens)
            self.span.set_data("ai.total_tokens", total)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.duration_ms = (time.time() - self.start_time) * 1000
        if self.span:
            self.span.__exit__(exc_type, exc_val, exc_tb)
        if exc_val and settings.sentry_dsn:
            sentry_sdk.capture_exception(exc_val)
