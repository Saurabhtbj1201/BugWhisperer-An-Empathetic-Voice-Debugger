---
title: BugWhisperer: An Empathetic Voice Debugger for My ADHD Friend Built with Gemma 2 & ElevenLabs
published: true
tags: devchallenge, weekendchallenge, hf26challenge, hacktoberfest
---

*This is a submission for the [Hacktoberfest Weekend Challenge: Build for a Friend](https://dev.to/challenges/hacktoberfest-weekend-2026-10-01)*

## What I Built

I built **BugWhisperer** for my friend, a talented developer who lives with ADHD.

For neurodivergent developers, a build failure isn't just an inconvenience—it's an ambush. An unexpected 80-line red stack trace flooding the terminal triggers acute cognitive overload, rapid heartbeat, and decision paralysis. The traditional workaround—switching tabs to paste logs into ChatGPT or search through Stack Overflow—breaks hyper-focus flow states and pulls developers into hour-long context-switching spirals.

**BugWhisperer** turns chaotic debugging into a calm, reassuring conversation. Whether piped directly from the terminal or pasted into its distraction-free companion dashboard, BugWhisperer uses **Google's Gemma 2** to strip the noise, explain the root cause in plain English, and provide **exactly ONE bite-sized next step**. 

Then, using **ElevenLabs**, it speaks the guidance aloud in a warm, calming cadence—acting just like an empathetic senior developer sitting beside you, whispering: *"Take a breath. You're doing great. It's just a missing null check on line 42."*

---

## Demo

- 🌐 **Live Web Companion**: [https://bugwhisperer.onrender.com](https://bugwhisperer.onrender.com) *(Hosted on Render)*
- 💻 **Terminal CLI Pipe**: `npm test 2>&1 | python cli/bugwhisper.py`

### What my friend said when testing it:
> *"When my build broke, hearing a calm voice validate that this happens to everyone before giving me just ONE thing to fix made my anxiety drop instantly. I didn't have to read through 40 lines of Webpack noise."* — my friend

---

## Code

{% github your-github-username/bugwhisperer %}

---

## How I Built It

BugWhisperer is built with a lightweight Python FastAPI backend, a glassmorphic HTML/Vanilla CSS frontend with real-time Web Audio API waveform visualization, and a terminal CLI pipe utility.

1. **Open-Source AI Core (Gemma 2)**:
   - We utilized **Gemma 2 (9B / 2B)** conditioned with a specialized ADHD Cognitive Pacing system prompt.
   - Standard LLMs generate 500-word academic explanations with multiple conflicting suggestions. BugWhisperer forces Gemma into a strict schema: (1) Empathy note, (2) Plain-English root cause (max 2 sentences), (3) Single actionable fix, and (4) Spoken script formatted for natural human listening (stripping raw syntax punctuation).
   - Designed to run seamlessly with **Ollama** locally for complete offline operation or cloud inference.

2. **Voice Engine (ElevenLabs)**:
   - The generated spoken script is synthesized via ElevenLabs Turbo v2.5 (`EXAVITQu4vr4xnSDxMaL` / Bella voice), optimized for stability and empathetic conversational cadence.
   - Built-in graceful fallback to the browser Web Speech API ensures audio guidance works even without external API credentials.

3. **Log Sanitization & Privacy**:
   - Strips ANSI terminal color escape codes and automatically sanitizes private filepaths (e.g. `C:\Users\username\...` to `~/project/...`).

4. **Observability (Sentry Agent Tracing)**:
   - Integrated the Sentry SDK to monitor LLM token consumption, inference latency, and voice roundtrips across debugging sessions.

---

## Why Does Open Innovation Matter?

Open innovation is what makes BugWhisperer both viable and ethical:

1. **Code Privacy & Intellectual Property**:
   Developers regularly work with proprietary codebase logs, secret environment variables, and client intellectual property. Sending raw stack traces to proprietary corporate APIs creates compliance and security liabilities. Gemma 2 can run **100% locally on a developer's machine** with zero telemetry leaving the device.

2. **Zero Subscription Paywalls for Accessibility**:
   Neurodivergent accessibility tools shouldn't be locked behind an ongoing $20/month proprietary API tax. Open weights democratize developer wellbeing.

3. **Prompt & Behavior Sovereignty**:
   With open weights, our custom ADHD cognitive pacing remains reproducible and consistent—free from arbitrary corporate RLHF shifts or unexpected model deprecations.

---

## Prize Categories

- **Best Use of Gemma (Featured - $200)**: Gemma 2 is the core reasoning brain powering the log diagnosis, plain-English translation, and spoken conversational script.
- **Best Use of Render (Featured - $200)**: Deployed on Render using Infrastructure as Code (`render.yaml`).
- **Best Use of ElevenLabs (Partner - $100)**: Empathetic audio synthesis giving voice to the rubber-duck companion.
- **Best Use of Sentry Agent Tracing (Partner - $100)**: Telemetry and span tracing capturing token usage and latency metrics.
