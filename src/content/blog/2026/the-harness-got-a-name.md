---
title: "The Harness Got a Name"
description: "A new survey and Microsoft's BUILD 2026 release both landed on the same idea: agent capability is leaving the model and moving into the harness."
pubDatetime: 2026-06-15T11:00:00-07:00
tags:
  - agents
  - harness
  - infrastructure
  - runtime
  - skills
featured: false
draft: false
---

Two things happened this month that, taken together, mark a quiet phase change in how agents are built. A 54-page survey gave the runtime around the model a formal name — the *harness* — and argued it is now where capability actually lives. A week later, Microsoft shipped a product literally called **Agent Harness**, with the survey's abstractions turned into concrete runtime classes. When the academics naming a thing and the vendors productizing it converge in the same fortnight, it usually means the field has stopped arguing about whether the idea is real.

The idea is this: for two years we made agents better by making models smarter. That lever is still useful, but it is no longer the main one. The main one is moving cognitive work *out* of the weights and into the system that surrounds them — and that system is finally being engineered as a first-class artifact instead of treated as glue.

## Externalization is the actual through-line

The survey that crystallizes this is [Externalization in LLM Agents](https://arxiv.org/abs/2604.08224) (Shanghai Jiao Tong, CMU, Sun Yat-Sen, and others, submitted April 9). Its framing is the most useful single sentence I've read about agent architecture this year: agents now improve "less by changing model weights than by reorganizing the runtime around them." Capabilities earlier systems expected the model to recover internally — remembering what happened ten steps ago, knowing the right procedure, following an interaction contract — are being pushed outward into four distinct stores:

- **Memory** externalizes state across time.
- **Skills** externalize procedural expertise.
- **Protocols** externalize interaction structure.
- **Harness engineering** is the unification layer that coordinates the other three into governed execution.

The paper traces a historical arc — *weights → context → harness* — and that arc is the part worth internalizing. The weights phase baked capability into parameters. The context phase (RAG, long windows, prompt engineering) moved it into what you put in front of the model at inference. The harness phase moves it into a persistent, programmable runtime that decides what enters context, when tools run, how state survives, and what the model is even allowed to do. The model is now one component in a system, not the system.

What makes the externalization frame more than a relabeling is its reliability claim: these external components aren't auxiliary, they "transform hard cognitive burdens into forms the model can solve more reliably." That dovetails with the separate finding from [Towards a Science of AI Agent Reliability](https://arxiv.org/abs/2602.16666v1) that raw capability gains barely move consistency or robustness. If smarter weights don't buy reliability, the harness is where reliability has to be bought instead.

## The abstractions just became runtime classes

The reason this stopped being a survey curiosity is timing. At [BUILD 2026](https://devblogs.microsoft.com/agent-framework/microsoft-agent-framework-at-build-2026-announce/), Microsoft Agent Framework — which hit [1.0 GA on April 2](https://techcommunity.microsoft.com/blog/azuredevcommunityblog/the-future-of-agentic-ai-inside-microsoft-agent-framework-1-0/4510698) by merging AutoGen and Semantic Kernel — shipped a layer named **Agent Harness**. Read its providers against the survey's four forms and the mapping is almost one-to-one: `FileMemoryProvider` (memory), `AgentSkillsProvider` (skills), `TodoProvider` and `AgentModeProvider` (interaction structure), plus automatic context compaction that watches token usage across long tool-calling chains, a `ToolApprovalAgent` middleware for sensitive operations, and OpenTelemetry tracing baked in.

This is the externalization thesis with a NuGet package. The interesting tell is *compaction as a default*: the harness, not the model, now owns the decision of what stays in the window. That used to be a prompt-engineering chore; it's now a runtime responsibility with a knob.

Sitting alongside it is **CodeAct**, where the model emits Python that calls tools via `call_tool()` inside a sandboxed Hyperlight micro-VM instead of emitting one JSON tool call per turn. Microsoft reports 52.4% faster execution and 63.9% fewer tokens on multi-step workloads. CodeAct is itself an externalization move — the *control flow* of a multi-tool task leaves the token stream and becomes code the harness executes. The model stops narrating every step and starts writing a program the runtime runs.

## What this changes for people building agents

Three practical consequences follow if you buy the framing.

First, **the harness is now the unit you version, test, and observe** — not the prompt and not the model. A model swap should be a config change against a stable harness, not a rewrite. If swapping models breaks your agent, your capability is still trapped in the weights and you have externalization debt.

Second, **the surrounding research stops looking like separate fields.** The shift from single-tool calls to [multi-tool orchestration](https://arxiv.org/abs/2603.22862) is a harness problem. The credit-assignment work in [agentic RL surveys](https://arxiv.org/html/2604.27859) is about what the weights still must learn *once* the harness has absorbed everything externalizable. Memory systems, skill registries, and protocols like MCP are all the same project viewed from different doors.

Third, **the harness is becoming the lock-in surface.** Whoever owns your memory provider, your skill format, and your compaction policy owns your agent's behavior more than your model vendor does. That is a procurement decision most teams are making implicitly right now, by picking a framework, without realizing it is the decision.

The blunt version: in mid-2026, "which model?" is a tuning question. "Which harness?" is the architecture.

## Worth bookmarking

- [Externalization in LLM Agents](https://arxiv.org/abs/2604.08224) — the survey that names the weights → context → harness progression.
- [Microsoft Agent Framework at BUILD 2026](https://devblogs.microsoft.com/agent-framework/microsoft-agent-framework-at-build-2026-announce/) — Agent Harness, Hosted Agents, and CodeAct.
- [Towards a Science of AI Agent Reliability](https://arxiv.org/abs/2602.16666v1) — why smarter weights don't buy dependability.
- [The Evolution of Tool Use in LLM Agents](https://arxiv.org/abs/2603.22862) — single-tool call to multi-tool orchestration.
- [Agentic RL: a brief overview](https://arxiv.org/html/2604.27859) — what the model still has to learn after externalization.
