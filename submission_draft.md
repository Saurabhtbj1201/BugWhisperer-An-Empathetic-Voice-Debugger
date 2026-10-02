---
title: BugWhisperer: A Voice-First Rubber-Duck Debugger for My ADHD Friend Built with Gemma 2 & ElevenLabs
published: true
tags: devchallenge, weekendchallenge, hf26challenge, hacktoberfest
cover_image: https://raw.githubusercontent.com/Saurabhtbj1201/BugWhisperer-An-Empathetic-Voice-Debugger/main/preview.png
---

*This is a submission for the [Hacktoberfest Weekend Challenge: Build for a Friend](https://dev.to/challenges/hacktoberfest-weekend-2026-10-01)*

---

## What I Built

I built **BugWhisperer** for my friend, a remarkably talented software engineer who lives with **ADHD**.

For neurodivergent builders, a broken build isn't merely an inconvenience—it's an ambush. When an unexpected 80-line red stack trace floods the terminal, it triggers immediate cognitive overload, rapid heartbeat, and decision paralysis. Staring into dense call frames feels visually overwhelming, and the common workaround—switching tabs to dump logs into ChatGPT or scan Stack Overflow—breaks hyper-focus flow states and pulls developers into hour-long context-switching rabbit holes.

**BugWhisperer** transforms chaotic terminal errors into a **calm, empathetic audio conversation**. 

Whether piped directly from your terminal (`pytest 2>&1 | python cli/bugwhisper.py`) or pasted into the distraction-free web dashboard, BugWhisperer uses **Google's Gemma 2** to strip away the noise, explain the root cause in plain English, and isolate **THE ONE next action** to take. 

Then, powered by **ElevenLabs Turbo v2.5**, it speaks the guidance aloud in a warm, reassuring human tone—acting like an empathetic senior pair programmer sitting right beside you, saying: 

> *"Take a breath. You're doing great. It's just a missing null-check on line 42."*

---

## Demo

- 🌐 **Live Web Companion**: [https://bugwhisperer.onrender.com](https://bugwhisperer.onrender.com/) *(Hosted on Render)*
- 💻 **Terminal CLI Pipe**: `npm test 2>&1 | python cli/bugwhisper.py`
- 📑 **Project Case Study**: [gu-saurabh.tech/project/8babe8cb-294b-48c5-8e29-3d280992cefa](https://www.gu-saurabh.tech/project/8babe8cb-294b-48c5-8e29-3d280992cefa)

![BugWhisperer Light Interface](https://raw.githubusercontent.com/Saurabhtbj1201/BugWhisperer-An-Empathetic-Voice-Debugger/main/preview.png)

### What my friend said when testing it:
> *"When my build broke, hearing a calm voice validate that this happens to everyone before giving me just ONE thing to fix made my anxiety drop instantly. I didn't have to read through 40 lines of Webpack noise."* — my friend

---

## Code

{% github Saurabhtbj1201/BugWhisperer-An-Empathetic-Voice-Debugger %}

---

## How I Built It

BugWhisperer is designed from the ground up for minimal cognitive load. The stack combines a lightweight **Python FastAPI** backend, a sharp **light-orange companion dashboard**, real-time **Web Audio API** waveform rendering, and a native **CLI pipe utility**.

### 1. Open-Source AI Core (Gemma 2)
Standard LLMs produce 500-word academic lectures with 5 different possibilities, which paralyzes someone with ADHD. We conditioned **Google Gemma 2 (9B / 2B)** with a specialized Cognitive Pacing Schema:
1. **Empathy First**: A short validation note to regulate stress.
2. **Plain-English Cause**: Two sentences maximum, stripping technical jargon.
3. **The Single Next Action**: Only **one** line of code or one file to inspect. No choice overload.
4. **Conversational Spoken Script**: Formatted specifically for audio synthesis (removing raw syntax characters like `{}`, `=>`, or unpronounceable regex tokens).

### 2. Voice Engine (ElevenLabs Turbo v2.5)
The generated spoken script streams through **ElevenLabs Turbo v2.5** using an empathetic voice profile tuned for calm pacing and reassurance. The frontend includes an automatic graceful fallback to the browser Web Speech API, ensuring full offline accessibility.

### 3. Log Sanitizer & Privacy Shield
Before any log reaches the AI engine, an automated sanitizer strips ANSI terminal escape sequences and masks local filepaths (e.g., `C:\Users\username\...` → `~/...`), protecting sensitive user directories.

### 4. Observability & Telemetry (Sentry Agent Tracing)
Every debugging interaction is traced using the **Sentry SDK**. Sentry records custom AI agent spans, measuring token consumption, LLM reasoning latency, and ElevenLabs audio roundtrip latency.

---

## Why Does Open Innovation Matter?

Open-source AI isn't an implementation detail in BugWhisperer; it is the reason the project can exist:

1. **Confidentiality & Code Privacy**:
   Developers routinely debug proprietary code containing internal API routes, business logic, and private filepaths. Sending full stack traces to closed corporate APIs creates immense compliance and security liabilities. With Gemma 2, developers can run inference **100% locally via Ollama** on their machine—no logs ever leave the local network.

2. **Zero Subscription Paywall for Accessibility**:
   Neurodivergent assistive tools should not require an ongoing $20/month proprietary API tax. Open weights democratize developer accessibility for students and independent builders worldwide.

3. **Prompt & Behavior Sovereignty**:
   Closed APIs regularly shift their behavior and prompt responses without notice. By anchoring on open weights, BugWhisperer’s tailored cognitive pacing remains consistent, auditable, and reliable over time.

---

## My Agent Session

This project was pair-programmed and architected using an AI coding agent session. The session drove the iterative design from the initial concept:
- Rapid prototyping of the ADHD cognitive prompt schema with Gemma 2.
- Structuring the dual-interface workflow (CLI pipe utility + modern light-orange companion dashboard).
- Implementing Sentry agent telemetry and ElevenLabs audio streaming.
- Refining the user interface based on neurodivergent accessibility feedback: replacing visual clutter with sharp, high-contrast action cards, a step-by-step parsing indicator, and a one-click Deep Focus Mode.

---

## Prize Categories

I am submitting BugWhisperer for the following partner categories:

- 🌟 **Best Use of Gemma (Featured - $200)**: Google Gemma 2 is the core reasoning brain powering the log diagnosis, plain-English translation, and spoken conversational script.
- 🚀 **Best Use of Render (Featured - $200)**: Fully automated deployment on Render using Infrastructure as Code (`render.yaml`).
- 🎙️ **Best Use of ElevenLabs (Partner - $100)**: Turbo v2.5 voice synthesis giving voice to the rubber-duck companion.
- 📊 **Best Use of Sentry Agent Tracing (Partner - $100)**: Telemetry and span tracing capturing token usage and latency metrics.

---

*How do you handle developer anxiety and cognitive overload during marathon debugging sessions? I'd love to hear your thoughts and feedback in the comments!*
