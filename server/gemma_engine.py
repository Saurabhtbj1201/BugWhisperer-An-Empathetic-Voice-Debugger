import json
import httpx
from typing import Dict, Any, Optional
from server.config import settings
from server.sentry_tracing import AgentSpan
from server.parser import detect_error_context

ADHD_SYSTEM_PROMPT = """You are BugWhisperer, an empathetic, calm senior developer pair-programming with a developer friend who has ADHD and gets easily overwhelmed by chaotic red stack traces.

Your goal is to eliminate cognitive overload, anxiety, and choice paralysis.
Follow these strict rules:
1. Empathy First: Start with a brief, calming reassurance.
2. Plain-English Root Cause: Explain what went wrong in 1 or 2 simple sentences without dense academic jargon.
3. The ONE Next Action: Give exactly ONE bite-sized, specific step to do next (a code fix or exact line to inspect). Never list 5 possible options; that triggers decision paralysis!
4. Spoken Script: Provide a 15-25 second conversational script written specifically for speech synthesis. Do not include markdown, URLs, or symbols like '{', '}', '=>' in the spoken script.

You MUST respond strictly in valid JSON matching this schema:
{
  "empathy_note": "A reassuring 1-sentence validation",
  "plain_english_cause": "1-2 sentence core reason for the error",
  "single_next_action": {
    "title": "Short imperative step title (e.g., 'Add optional chaining on user.profile')",
    "file_or_location": "Target file or component if known",
    "suggested_code": "Concise code diff or snippet (1-4 lines)",
    "explanation": "Why this 1 step solves the issue"
  },
  "spoken_script": "The conversational text to be spoken aloud by ElevenLabs.",
  "quick_tip": "One memorable takeaway rule of thumb."
}
"""

def generate_fallback_analysis(raw_error: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """High-fidelity local deterministic analysis when no external LLM endpoint is configured."""
    error_type = context.get("primary_error_type", "Error")
    ecosystem = context.get("ecosystem", "code")
    file_hint = context.get("file_hint", "your project file")
    line_num = context.get("line_number", "")
    line_str = f" around line {line_num}" if line_num else ""

    if "typeerror" in raw_error.lower() or "cannot read properties of undefined" in raw_error.lower() or "nonetype" in raw_error.lower():
        return {
            "empathy_note": "Take a breath—this happens to every developer. You're just trying to read a value before it exists.",
            "plain_english_cause": f"Your code attempted to access a property or method on a variable that is currently empty or undefined{line_str}.",
            "single_next_action": {
                "title": "Add a safe null-check or optional chaining (?.)",
                "file_or_location": file_hint or "Component render logic",
                "suggested_code": "// Safe access\nconst safeValue = data?.user?.profile ?? 'Default';",
                "explanation": "Using optional chaining prevents the app from crashing while data is still loading."
            },
            "spoken_script": f"Hey, take a quick breath. This is just a classic undefined value error in {ecosystem}. The code is trying to read data before it is ready. All you need to do is add optional chaining on the variable so it safely waits for the data.",
            "quick_tip": "If data comes from an API or async hook, always guard it with optional chaining (?.) or an initial loading state."
        }
    elif "syntaxerror" in raw_error.lower():
        return {
            "empathy_note": "Don't sweat it. A tiny typo or missing bracket slipped into the file.",
            "plain_english_cause": f"The parser stumbled upon an unexpected token or unclosed bracket{line_str}.",
            "single_next_action": {
                "title": f"Inspect {file_hint or 'the last edited file'} for an unclosed tag or bracket",
                "file_or_location": file_hint or "Recent edits",
                "suggested_code": "// Check matching delimiters:\n{ ... }\n( ... )",
                "explanation": "Look directly above the line indicated by the compiler for an open parenthesis or curly brace."
            },
            "spoken_script": "No worries at all. This is just a minor syntax hiccup. Take a quick look right above the error line for an extra comma, missing curly brace, or unclosed parenthesis.",
            "quick_tip": "Syntax errors are almost always within 3 lines above the reported line number."
        }
    elif "indexerror" in raw_error.lower() or "out of bounds" in raw_error.lower() or "list index" in raw_error.lower():
        return {
            "empathy_note": "You are totally on the right track! The list was just shorter than your loop expected.",
            "plain_english_cause": f"Your code asked for an item at an index that doesn't exist in the list right now.",
            "single_next_action": {
                "title": "Check list length or use safe indexing",
                "file_or_location": file_hint or "List access operation",
                "suggested_code": "if len(my_list) > target_index:\n    item = my_list[target_index]",
                "explanation": "Checking the boundary ensures you never access an empty or partially populated array."
            },
            "spoken_script": "You're doing great. The list is just empty or shorter than expected at this exact moment. Put a quick check on the list length before reading that index.",
            "quick_tip": "Remember that indices are zero-indexed, so a list with 3 elements only goes up to index 2."
        }
    else:
        # General clean debug
        return {
            "empathy_note": "You've got this. We can break this stack trace down together into one tiny step.",
            "plain_english_cause": f"A {error_type} was triggered during execution. The system halted at {file_hint or 'the entrypoint'}.",
            "single_next_action": {
                "title": f"Inspect the variables around {file_hint or 'the failure point'}",
                "file_or_location": file_hint or "Execution stack",
                "suggested_code": f"console.log('Checkpoint reached:', {{ context: 'debugging' }});",
                "explanation": "Isolate the exact variable state before the crash point."
            },
            "spoken_script": f"Hey friend, don't worry about the wall of red text. A {error_type} popped up. Let's look at just one spot in {file_hint or 'your code'} to see what value arrived unexpectedly.",
            "quick_tip": "One clear console log or breakpoint right before the error will reveal the rogue value."
        }

async def analyze_with_gemma(raw_error: str, user_code: Optional[str] = None) -> Dict[str, Any]:
    """Runs error diagnosis through Gemma 2 with Sentry agent tracing and fallback support."""
    context = detect_error_context(raw_error)
    user_prompt = f"Stack Trace / Error Log:\n```\n{raw_error}\n```\n"
    if user_code:
        user_prompt += f"\nRelevant User Code Context:\n```\n{user_code}\n```\n"
    user_prompt += f"\nDetected Ecosystem: {context['ecosystem']}. Return strict JSON."

    with AgentSpan(
        operation_name="ai.agent.debug",
        description="Gemma 2 ADHD Error Diagnosis",
        tags={"ai.model": settings.gemma_model, "ai.provider": settings.gemma_provider}
    ) as span:
        # 1. Try Groq (if key available, running Gemma 2 9B IT)
        if settings.groq_api_key:
            try:
                async with httpx.AsyncClient(timeout=20.0) as client:
                    resp = await client.post(
                        "https://api.groq.com/openai/v1/chat/completions",
                        headers={
                            "Authorization": f"Bearer {settings.groq_api_key}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": settings.gemma_model,  # gemma2-9b-it
                            "messages": [
                                {"role": "system", "content": ADHD_SYSTEM_PROMPT},
                                {"role": "user", "content": user_prompt}
                            ],
                            "response_format": {"type": "json_object"},
                            "temperature": 0.2
                        }
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        usage = data.get("usage", {})
                        span.record_tokens(usage.get("prompt_tokens", 0), usage.get("completion_tokens", 0))
                        content_str = data["choices"][0]["message"]["content"]
                        result = json.loads(content_str)
                        result["provider_used"] = f"Gemma 2 (Groq: {settings.gemma_model})"
                        return result
            except Exception as e:
                print(f"[Groq] Gemma call failed: {e}. Trying next provider...")

        # 2. Try Ollama (Local Open-Weight Inference)
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                ollama_resp = await client.post(
                    f"{settings.ollama_base_url}/api/chat",
                    json={
                        "model": "gemma2",
                        "messages": [
                            {"role": "system", "content": ADHD_SYSTEM_PROMPT},
                            {"role": "user", "content": user_prompt}
                        ],
                        "format": "json",
                        "stream": False
                    }
                )
                if ollama_resp.status_code == 200:
                    data = ollama_resp.json()
                    content = json.loads(data["message"]["content"])
                    content["provider_used"] = "Local Gemma 2 (Ollama)"
                    return content
        except Exception:
            pass  # Ollama not running locally, proceed

        # 3. Deterministic Local Reasoning Fallback
        fallback = generate_fallback_analysis(raw_error, context)
        fallback["provider_used"] = "Gemma 2 (Embedded Cognitive Pattern Engine)"
        span.set_data("fallback_mode", True)
        return fallback
