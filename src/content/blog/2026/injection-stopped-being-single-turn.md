---
title: "Injection Stopped Being a Single-Turn Problem"
description: "Once agents got long-term memory, a one-time prompt injection could survive across sessions. Mid-2026 research shows both the attack and the defense moving up the stack."
pubDatetime: 2026-06-20T11:00:00-07:00
tags:
  - agents
  - security
  - prompt-injection
  - memory
featured: false
draft: false
---

For two years, the mental model for prompt injection was a single bad turn: untrusted content sneaks an instruction into the context window, the model follows it, and the blast radius ends when the conversation does. Clear the session and you cleared the problem. A run of papers over the last few months kills that assumption. The moment you give an agent durable memory and let it rewrite its own state, a one-time injection can become a permanent one. Injection is no longer an event you survive — it's a condition the agent can carry.

This matters because the rest of the stack has been racing in exactly the direction that makes it worse. Persistent memory, self-written skills, and long-horizon trajectories are the features everyone is shipping. They are also the substrate that turns a transient attack into a resident one.

## Memory converted a one-shot exploit into tenancy

The clearest statement of the new threat is [Zombie Agents](https://arxiv.org/abs/2602.15654), which studies what happens when injection meets a self-evolving agent. The attack has two phases: an infection phase, where poisoned content arrives as ordinary external data and gets absorbed into long-term memory during normal operation, and a trigger phase, where the stored payload later fires unauthorized actions. The authors' framing is the part worth tattooing on the wall: "memory evolution can convert one-time indirect injection into persistent compromise." The agent isn't re-attacked each time. It re-attacks itself, because the malicious instruction is now part of what it considers its own accumulated experience.

This is the dark mirror of every memory-and-skills feature being celebrated right now. The same mechanism that lets an agent remember a user preference or promote a useful pattern into a reusable skill is a write path into durable state — and write paths fed by untrusted content are exactly where you don't want unconstrained text flowing. We have spent a year building memory as infrastructure. We mostly have not built provenance for what gets written into it.

## The attack side professionalized

The other thing that changed is that injection stopped being an artisanal craft of clever strings. [IterInject](https://arxiv.org/abs/2605.24659), posted in late May, treats indirect prompt injection as an optimization loop: a diagnoser labels each failed attempt with structured behavioral descriptions, an optimizer refines the payload conditioned on the full history, and the system mines new attack seeds from failure patterns to grow its own template bank. It outperforms static baselines on the AgentDojo and InjectAgent benchmarks, and — the detail that should make you uncomfortable — it landed full success on five of nine targets against Claude Code, a production agent, while surfacing an attention-mediated threshold mechanism in the model's mid-to-late layers.

Put the two papers together and the shape is obvious. Attackers now have an automated loop for finding payloads that get past a real agent, and a memory architecture that makes any single success persistent. The economics flip: you no longer need a payload that works every time, only one that works once and gets remembered.

## Defenses are moving from filtering text to constraining structure

The encouraging counter-trend is that the better defenses have stopped trying to detect bad text and started constraining what the data-to-action path is allowed to do. Three approaches from this year sketch the design space.

[AgentSentry](https://arxiv.org/abs/2602.22724) treats injection as something you diagnose causally rather than match lexically. At each tool-return boundary it runs controlled counterfactual re-executions to find where the agent's behavior was actually hijacked, then applies "context purification" to strip the attack-induced deviation while keeping the task-relevant information, so the workflow continues instead of aborting. It reports a 74.55% utility-under-attack score — notable because it optimizes for staying useful while compromised, not just for refusing.

[IPIGuard](https://arxiv.org/abs/2508.15310) goes structural in a different way, building a tool-dependency graph so the agent's planned actions are checked against an expected call structure rather than against the content of any single tool result. And the [tool-result-parsing defense](https://arxiv.org/abs/2601.04795) from January takes the bluntest line: parse tool output into precise typed data and feed the model that, filtering injected instruction-like text before it ever reaches the context. Different mechanisms, one shared instinct — the trust boundary belongs at the seam between tool output and model input, not inside the model's judgment.

## What to actually change

The takeaway for anyone running agents in production is that session-scoped guardrails are now necessary but no longer sufficient. If your agent has durable memory, the security questions worth asking are about writes, not just reads:

- **Where does untrusted content acquire write access to durable state?** Memory and self-authored skills are the high-value targets; treat any path from external data into them as privileged.
- **Can you attribute a memory or skill entry to its source?** Without provenance you cannot quarantine or roll back a poisoned write, and you cannot tell a learned preference from a planted instruction.
- **Are tool outputs typed before the model sees them?** The cheapest durable win is keeping instruction-shaped text out of the context window in the first place.
- **Do you constrain action structure, not just action content?** A dependency graph or capability scope catches the hijack the text filter missed.

Prompt injection remains, as the OWASP LLM Top 10 has said for two years running, the number-one risk — and it is not fully solvable inside current model architectures. What's new in mid-2026 is the realization that the dangerous version isn't the one that reads your context. It's the one that writes to it.

## Worth bookmarking

- [Zombie Agents: Persistent Control of Self-Evolving LLM Agents](https://arxiv.org/abs/2602.15654) — the memory-as-persistence threat model.
- [IterInject](https://arxiv.org/abs/2605.24659) — injection as a feedback-guided optimization loop, tested against Claude Code.
- [AgentSentry](https://arxiv.org/abs/2602.22724) — causal diagnostics and context purification at tool-return boundaries.
- [IPIGuard](https://arxiv.org/abs/2508.15310) — tool-dependency-graph defense that checks plan structure.
- [Defense via Tool Result Parsing](https://arxiv.org/abs/2601.04795) — type tool output before the model reads it.
