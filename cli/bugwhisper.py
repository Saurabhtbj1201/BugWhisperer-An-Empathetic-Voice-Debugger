#!/usr/bin/env python3
"""
BugWhisperer CLI: A voice-first rubber-duck companion for your terminal.
Usage:
  pytest 2>&1 | python cli/bugwhisper.py
  npm test 2>&1 | python cli/bugwhisper.py
  python cli/bugwhisper.py --sample python
"""

import sys
import os
import argparse
import subprocess
import httpx

# Ensure parent directory is in Python path for direct imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server.parser import sanitize_logs, detect_error_context
from server.gemma_engine import generate_fallback_analysis

SAMPLES = {
    "react": """TypeError: Cannot read properties of undefined (reading 'avatar')
    at UserProfileCard (UserProfile.tsx:42:25)
    at renderWithHooks (react-dom.development.js:15486:18)
    at mountIndeterminateComponent (react-dom.development.js:20103:13)
    at beginWork (react-dom.development.js:21626:16)""",
    "python": """Traceback (most recent call last):
  File "C:\\Users\\dev\\workspace\\app\\processor.py", line 87, in process_batch
    current_item = batch_items[idx]
IndexError: list index out of range"""
}

def speak_local(text: str):
    """Speaks the text using Windows SAPI TTS or macOS 'say' command."""
    try:
        clean_text = text.replace('"', '\\"').replace("'", "")
        if sys.platform == "win32":
            cmd = f'powershell -Command "Add-Type –AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak(\'{clean_text}\')"'
            subprocess.Popen(cmd, shell=True)
        elif sys.platform == "darwin":
            subprocess.Popen(["say", text])
    except Exception:
        pass

# Ensure utf-8 encoding on Windows terminal
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

def print_banner():
    print("=" * 60)
    print(" [BugWhisperer CLI] Calming Voice Debugger for ADHD Devs")
    print("=" * 60)

def print_result(diagnosis: dict):
    print("\n* BREATHE:", diagnosis.get("empathy_note", ""))
    print("\n* ROOT CAUSE:", diagnosis.get("plain_english_cause", ""))
    
    action = diagnosis.get("single_next_action", {})
    print("\n* THE ONE NEXT ACTION:")
    print(f"   > {action.get('title', '')}")
    if action.get("file_or_location"):
        print(f"   [File] {action.get('file_or_location')}")
    if action.get("suggested_code"):
        print("   [Fix]:")
        for line in action.get("suggested_code", "").split("\n"):
            print(f"      {line}")
            
    print(f"\n* QUICK TIP: {diagnosis.get('quick_tip', '')}")
    print("=" * 60 + "\n")


def main():
    parser = argparse.ArgumentParser(description="BugWhisperer: ADHD Voice Debugger")
    parser.add_argument("--sample", choices=["react", "python"], help="Run with a sample stack trace")
    parser.add_argument("--quiet", action="store_true", help="Disable voice audio output")
    parser.add_argument("error", nargs="*", help="Optional raw error string")
    args = parser.parse_args()

    print_banner()

    error_input = ""
    if args.sample:
        print(f"📋 Running sample: {args.sample.upper()}")
        error_input = SAMPLES[args.sample]
    elif args.error:
        error_input = " ".join(args.error)
    elif not sys.stdin.isatty():
        error_input = sys.stdin.read()

    if not error_input.strip():
        print("💡 No error input detected. Pipe an error or run:")
        print("   python cli/bugwhisper.py --sample react")
        print("   npm test 2>&1 | python cli/bugwhisper.py")
        sys.exit(0)

    sanitized = sanitize_logs(error_input)
    
    # Try calling the running FastAPI server, or use local fallback
    diagnosis = None
    try:
        resp = httpx.post("http://localhost:8000/api/debug", json={"error_log": sanitized, "with_voice": False}, timeout=3.0)
        if resp.status_code == 200:
            diagnosis = resp.json().get("diagnosis")
    except Exception:
        pass

    if not diagnosis:
        context = detect_error_context(sanitized)
        diagnosis = generate_fallback_analysis(sanitized, context)

    print_result(diagnosis)

    if not args.quiet and "spoken_script" in diagnosis:
        print("🎙️ Speaking audio guidance...")
        speak_local(diagnosis["spoken_script"])

if __name__ == "__main__":
    main()
