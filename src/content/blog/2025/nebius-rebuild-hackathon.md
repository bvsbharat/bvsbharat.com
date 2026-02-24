---
title: "Winner — EchoForge Studio at Nebius Rebuild Hackathon"
description: "Built EchoForge Studio — AI-driven voice agents with full transparency and user control. Proving that powerful AI doesn't have to be a black box."
pubDatetime: 2025-02-15T00:00:00Z
tags:
  - hackathon
  - voice-ai
  - ai
  - agents
featured: true
---

In a world where AI often feels like a black box, we set out to create something different — AI-driven voice agents with full transparency and user control.

<div style="position:relative;padding-bottom:56.25%;height:0;overflow:hidden;margin:2rem 0;">
  <iframe src="https://www.youtube.com/embed/Jzhi_yBathI" style="position:absolute;top:0;left:0;width:100%;height:100%;border:0;" allowfullscreen></iframe>
</div>

## What We Built

**EchoForge Studio** — a platform for building transparent, customizable AI voice agents. Unlike traditional voice AI systems that hide their decision-making behind opaque models, EchoForge gives users clear explanations of AI decisions and granular control over agent behavior.

### Architecture

The system is built around three core principles — transparency, control, and quality:

1. **Decision Transparency Layer** — Every AI decision is logged with reasoning traces. When the voice agent routes a conversation, changes tone, or triggers an action, users can see exactly why and adjust the behavior.

2. **Customization Engine** — Granular controls for voice parameters (tone, pace, personality), conversation flow logic, escalation rules, and response templates. Users design agent behavior through an intuitive interface rather than writing prompts.

3. **Real-Time Voice Pipeline** — Low-latency voice processing using streaming ASR (automatic speech recognition), LLM-based intent understanding, and neural TTS (text-to-speech) for natural conversations.

### Technical Stack

- **Voice Processing** — WebRTC for real-time audio streaming, Whisper for transcription
- **Agent Logic** — LangGraph for conversation state management and decision routing
- **LLM Integration** — Multi-model support with explainable output generation
- **Frontend** — React with real-time waveform visualization and decision trace UI
- **Infrastructure** — Nebius cloud for GPU-accelerated inference

### Key Capabilities

- **Explainable Decisions** — Visual decision traces showing why the agent took each action
- **Live Customization** — Adjust agent behavior in real-time without redeploying
- **Voice Personality Designer** — Configure tone, speaking style, and emotional responses
- **Conversation Flow Builder** — Visual editor for designing multi-turn conversation logic
- **Audit Trail** — Complete log of every interaction with reasoning annotations

## Why Transparency Matters

Most voice AI platforms treat their agents as black boxes — you get output, but no visibility into why. This creates trust issues, especially in enterprise contexts where compliance and auditability matter. EchoForge Studio proves that powerful AI and transparency aren't mutually exclusive.

## Acknowledgments

Thanks to the organizers at **Sprint.dev** and **Nebius** for hosting the Rebuild Hackathon and pushing for a more open, user-centric AI future.

[Watch the demo](https://lnkd.in/gVGEDkhq)
