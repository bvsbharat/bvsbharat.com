---
title: "The Trajectory Became the Cost Center"
description: "A wave of mid-2026 research stopped trying to make the model cheaper and started compressing the agent's own trajectory — at the observation, action, and skill level."
pubDatetime: 2026-06-06T11:00:00-07:00
tags:
  - agents
  - efficiency
  - context-engineering
  - cost-optimization
  - research
featured: false
draft: false
---

For two years the standard way to make an agent cheaper was to make the model cheaper: route easy turns to a small model, distill, cache the system prompt. Those moves still work, but they all treat the agent's accumulating context as a fixed input you pay to re-read on every step. The research that landed over the past several weeks rejects that assumption. The new target isn't the model — it's the trajectory itself. The cheapest token is the one the agent never has to read again.

This is a sharper claim than "context engineering," which is mostly about what you put *into* the window. The 2026 efficiency wave is about what you take *out*, mid-run, without the agent noticing. Three groups of papers attack the same accumulating bill from three different altitudes, and a fourth set of work argues the whole edifice is overbuilt to begin with.

## The bill grows with the step count, not the task

The core economic fact of a ReAct-style loop is unglamorous: input tokens grow roughly linearly with the number of steps, because every step re-sends the full history. An 18-step task doesn't cost 18× a single call — it costs the *integral* of a growing context. That integral, not output generation, is where most of the money goes.

[AgentDiet](https://arxiv.org/abs/2509.23586) (revised March 2026) is the cleanest demonstration. A cheap "reflection" LLM runs alongside the main agent on a sliding window, deleting three categories of cruft from older steps: useless output (cache dumps, verbose logs), redundant content repeated across steps, and expired details no longer relevant after the task moved on. The result is a 39.9–59.7% cut in input tokens and a 21.1–35.9% cut in total cost, with task success moving between −1.0% and +2.0%. The reflection module adds 5–10% overhead and still nets a large win. The important detail is *what* it preserves: error messages and causal action–observation links survive, because those are what the agent actually reasons over. You cannot treat a trajectory like a blog post and run generic text summarization on it — a [late-May preprint on context compression for agents](https://arxiv.org/abs/2510.00615) makes exactly this point, that distilling a trajectory means preserving causal dependencies between what the agent did and what it saw, not just shrinking word count.

If you've watched Claude Code's auto-compact fire at 95% context, you've seen the production version of this idea: summarize the trajectory, keep the architectural decisions and open bugs, drop the rest. The research is formalizing what tools already do by reflex.

## Compress at three altitudes

What's interesting is that the compression target keeps moving down the stack.

**Observations.** [TACO](https://arxiv.org/abs/2604.19572) (April 2026) compresses terminal-agent *observations* — the verbose stdout that floods the context after every shell command. Instead of static truncation heuristics, it learns task-specific compression rules, keeps the high-performing ones in a global pool, and backs off when it has cut too aggressively (it watches for dropped error messages). On TerminalBench it trims ~10% of per-step tokens on 200B+ models while *improving* accuracy 1–4 points — compression as a denoiser, not just a cost lever.

**Actions.** [Latent Action Reparameterization](https://arxiv.org/abs/2605.18597) (May 18) goes after the *action* sequence. The cost driver there is the long horizon of low-level textual actions; LAR learns a compact latent action space where one abstract action stands in for a multi-step behavior, shrinking the effective decision horizon. Fewer, denser actions mean fewer tokens and lower wall-clock latency at equal or better success.

**Skills.** [SkillReducer](https://arxiv.org/abs/2603.29919) attacks the descriptions themselves, compressing a skill's prose from 87 tokens to 32 — a 63% cut — so that an agent loading dozens of skill cards into context pays a fraction of the old tax. When skills are how you scale past the ~30-tool ceiling, the skill manifest *is* recurring context, and it compresses like everything else.

Observation, action, skill: the same instinct applied at every layer where text accumulates.

## The minimalist counterargument

There's a louder version of this argument that says the accumulation is self-inflicted. [Terminal Agents Suffice for Enterprise Automation](https://arxiv.org/abs/2604.00073) (March–April 2026) found that an agent with nothing but a terminal and a filesystem, hitting platform APIs directly, *matches or beats* tool-augmented MCP agents and GUI web agents on real enterprise tasks — at lower cost and operational overhead. Their point isn't anti-MCP dogma; it's that a lot of agentic complexity adds tokens and failure surface without adding capability that a strong model didn't already have. A [co-design study](https://arxiv.org/abs/2512.18337) reaches the efficiency conclusion from the systems side: rethinking the inference architecture alongside the agent loop cuts token usage 50%+ and latency 1.8–2.5×.

The two camps agree on the underlying claim. Compression people shrink the trajectory after the fact; minimalists keep it small by design. Both are betting that the dominant cost in a 2026 agent is the context it drags behind it, and both are right.

## Why this matters now

The reason to care this week rather than someday: efficiency is starting to become an *objective an agent optimizes*, not just a knob a human turns. The [Meta-Agent Challenge](https://arxiv.org/abs/2606.04455) (June 3) drops a code agent into a sandbox and asks it to *build another agent* that maximizes held-out performance under a time and compute budget. The moment the budget is in the loss, trajectory bloat stops being a billing annoyance and becomes a thing the meta-agent learns to avoid. The compression techniques above are the primitives those self-built agents will reach for.

Practical takeaway if you run agents in production: instrument cumulative input tokens per task, not just per call. If that number climbs faster than your task complexity, you're paying to re-read garbage, and there's now a literature on how to stop.

## Worth bookmarking

- [AgentDiet — Reducing Cost of LLM Agents with Trajectory Reduction](https://arxiv.org/abs/2509.23586)
- [TACO — Self-Evolving Observational Context Compression for Terminal Agents](https://arxiv.org/abs/2604.19572)
- [Latent Action Reparameterization for Efficient Agent Inference](https://arxiv.org/abs/2605.18597)
- [SkillReducer — Optimizing LLM Agent Skills for Token Efficiency](https://arxiv.org/abs/2603.29919)
- [Terminal Agents Suffice for Enterprise Automation](https://arxiv.org/abs/2604.00073)
- [The Meta-Agent Challenge](https://arxiv.org/abs/2606.04455)
