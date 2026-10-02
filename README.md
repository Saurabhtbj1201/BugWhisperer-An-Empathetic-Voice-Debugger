# 🦆 BugWhisperer

> **An empathetic, voice-first rubber-duck debugging companion built with Gemma 2, ElevenLabs, and Sentry for ADHD developers.**  
> *Created for the Hacktoberfest 2026 Weekend Challenge: "Build for a Friend"*

[![Render Deploy](https://img.shields.io/badge/Render-Deployed-brightgreen)](https://render.com)
[![Open Source AI](https://img.shields.io/badge/Open--Source%20AI-Gemma%202%20(Google)-blue)](https://ai.google.dev/gemma)
[![Voice](https://img.shields.io/badge/Voice-ElevenLabs%20Turbo%20v2.5-orange)](https://elevenlabs.io)
[![Observability](https://img.shields.io/badge/Telemetry-Sentry%20Agent%20Tracing-purple)](https://sentry.io)

---

## 🌟 The Story: Who I Built This For

My friend is a brilliant developer who has ADHD. When a build breaks or an 80-line red stack trace explodes in the terminal, it immediately triggers cognitive overload, analysis paralysis, and heart-pounding panic. 

Standard workflows make things worse:
- Reading long terminal logs is visually overstimulating.
- Tab-switching to ChatGPT or StackOverflow breaks the hyper-focus state and leads down endless rabbit holes.
- Traditional tools offer 5–10 theoretical causes instead of **the single next action**.

**BugWhisperer** solves this by turning chaotic errors into a **calm, spoken conversation** like having an empathetic senior mentor sitting next to you. It isolates the noise, gives you **only ONE actionable next step**, and speaks it soothingly.

---

## ✨ Key Features

- **🧘 Empathy & Pacing First**: Validates the developer with a reassuring breath note before diving into code.
- **🎯 The "ONE Next Action" Principle**: Never overwhelms with 5 choices. Isolates the single offending line and provides a minimal fix.
- **🎙️ Voice-First Delivery (ElevenLabs)**: Reads a custom-tailored, conversational audio script so you don't even have to read the screen.
- **🧠 Open-Weight AI Core (Gemma 2)**: Powered by Google's Gemma 2 (2B / 9B) open-weights.
- **🔒 Privacy Shield**: Automatically sanitizes local user paths (`C:\Users\username\...` -> `~/...`) and ANSI codes before processing.
- **🔕 Deep Focus Mode**: One-click toggle that strips away all distractions, leaving only the glowing 1-step fix.
- **💻 Dual Interface**: Modern Glassmorphic Web Companion + Terminal CLI pipe tool (`npm test 2>&1 | python cli/bugwhisper.py`).
- **📊 Sentry Agent Tracing**: Real-time observability tracking token consumption, agent latency, and voice roundtrips.

---

## 🏗️ Why Open Innovation Matters

1. **Client & Proprietary Code Privacy**: Closed APIs (like OpenAI) transmit proprietary enterprise stack traces and filepaths to remote corporate servers. With Gemma 2, developers can run inference 100% locally via Ollama or private endpoints.
2. **Zero Subscription Barrier**: Developers with ADHD or students should not be locked behind a $20/month paywall just to debug their code calmly.
3. **Custom Cognitive Prompt Conditioning**: Open models allow fine-tuning and strict system-prompting for cognitive ease and neurodivergent pacing without model deprecation surprises.

---

## 🚀 Quick Start

### 1. Clone & Install
```bash
git clone https://github.com/your-username/bugwhisperer.git
cd bugwhisperer
pip install -r server/requirements.txt
```

### 2. Configure Environment (Optional)
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
*Note: If no API keys are provided, BugWhisperer runs automatically in high-fidelity local cognitive fallback mode!*

### 3. Launch the Web Companion
```bash
python -m server.main
```
Open your browser to: **`http://localhost:8000`**

### 4. Or Use via Terminal CLI
```bash
# Pipe any command directly
npm test 2>&1 | python cli/bugwhisper.py

# Or test with sample presets
python cli/bugwhisper.py --sample react
python cli/bugwhisper.py --sample python
```

---

## 🏆 Hacktoberfest Prize Categories Entered

- **Best Use of Gemma ($200 - Featured)**: Uses Google Gemma 2 (9B/2B) with custom ADHD cognitive pacing prompt schemas for error diagnosis and spoken script generation.
- **Best Use of Render ($200 - Featured)**: Infrastructure-as-code deployment on Render web services via `render.yaml`.
- **Best Use of ElevenLabs ($100 - Partner)**: Turbo v2.5 voice synthesis providing empathetic, non-robotic audio companion pacing.
- **Best Use of Sentry Agent Tracing ($100 - Partner)**: Observability using Sentry SDK with custom agent spans, token tracking, and error telemetry.

---

## 📜 License
MIT License • Built with love for open-source AI and friends everywhere.
