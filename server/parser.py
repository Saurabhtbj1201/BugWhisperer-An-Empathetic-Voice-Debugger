import re
from typing import Dict, Any

ANSI_ESCAPE_PATTERN = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
WINDOWS_USER_PATH_PATTERN = re.compile(r'[A-Za-z]:\\[Uu]sers\\[^\\]+\\')
UNIX_USER_PATH_PATTERN = re.compile(r'/home/[^/]+/')

def sanitize_logs(raw_text: str) -> str:
    """Removes ANSI escape codes and masks private system paths."""
    if not raw_text:
        return ""
    # Strip ANSI colors
    cleaned = ANSI_ESCAPE_PATTERN.sub('', raw_text)
    # Mask user paths for privacy
    cleaned = WINDOWS_USER_PATH_PATTERN.sub('~/', cleaned)
    cleaned = UNIX_USER_PATH_PATTERN.sub('~/', cleaned)
    return cleaned.strip()

def detect_error_context(log_text: str) -> Dict[str, Any]:
    """Heuristically extracts key metadata to guide Gemma 2's reasoning."""
    context = {
        "ecosystem": "unknown",
        "primary_error_type": "Unknown Error",
        "file_hint": "",
        "line_number": None
    }
    
    text_lower = log_text.lower()
    
    # Ecosystem detection
    if "traceback (most recent call last)" in text_lower or ".py" in text_lower:
        context["ecosystem"] = "python"
        err_match = re.search(r'([A-Za-z0-9_]+Error|Exception): (.*)', log_text)
        if err_match:
            context["primary_error_type"] = err_match.group(1)
        file_match = re.findall(r'File "([^"]+)", line (\d+)', log_text)
        if file_match:
            context["file_hint"] = file_match[-1][0]
            context["line_number"] = int(file_match[-1][1])
            
    elif "typeerror" in text_lower or "referenceerror" in text_lower or "syntaxerror" in text_lower or ".js" in text_lower or ".ts" in text_lower or ".tsx" in text_lower:
        context["ecosystem"] = "javascript/typescript"
        err_match = re.search(r'([A-Za-z0-9_]+Error): (.*)', log_text)
        if err_match:
            context["primary_error_type"] = err_match.group(1)
            
    elif "cargo" in text_lower or "rustc" in text_lower or "panicked at" in text_lower:
        context["ecosystem"] = "rust"
        context["primary_error_type"] = "Rust Panic / Compilation Error"
        
    elif "docker" in text_lower or "container" in text_lower or "permission denied" in text_lower:
        context["ecosystem"] = "devops/docker"
        if "permission denied" in text_lower:
            context["primary_error_type"] = "PermissionDenied"
            
    return context
