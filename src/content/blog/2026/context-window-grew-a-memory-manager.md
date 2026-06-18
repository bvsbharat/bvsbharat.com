---
title: "The Context Window Grew a Memory Manager"
description: "A June 2026 wave of papers shows pruning beats full context on accuracy and cost — and that eviction is becoming a deterministic, cache-aware system, not a summarize call."
pubDatetime: 2026-06-18T11:00:00-07:00
tags:
  - agents
  - context-engineering
  - memory
  - inference
  - research
featured: false
draft: false
---

Here is the result that should reorganize how you think about agent context: feeding an agent its full history makes it *worse*, not just more expensive. In [Less Context, Better Agents](https://arxiv.org/abs/2606.10209) (June 8), agents that kept only the last five tool-call/response pairs plus a short rolling summary hit 91.6% task completion on a multi-turn expense workflow. The same agent with full history managed 71.0% — while burning 1.48M tokens and 14.5 hours per run. The failure analysis is the part to sit with: stale-state errors fell from 47% of failures under full context to 6% under pruning. The model wasn't running out of room. It was being actively confused by its own accumulated tool output.

For two years the default mental model has been that the context window is an upper bound you fill as fully as you can afford, and the only question is cost. A cluster of papers that landed in the first half of June 2026 retires that model. Context is now a managed resource with a working set, a lifecycle, and an eviction policy — and the agents that manage it well beat the agents that hoard on *both* accuracy and bill. The context window grew a memory manager, and it looks a lot like the one in your operating system.

## Eviction is becoming a policy, not a prompt

The reflexive fix for a full window is to ask the model to summarize and continue. That move has well-documented failure modes — it hallucinates, it loses causal structure, and it is itself an expensive non-deterministic LLM call inserted into your hot path. The new work routes around it.

[Beyond Compaction: Structured Context Eviction for Long-Horizon Agents](https://arxiv.org/abs/2606.11213) replaces summarization with a Context Window Lifecycle: the agent annotates its trajectory as typed, dependency-linked episodes as it works, and a *deterministic, LLM-free* policy evicts completed action episodes when the budget is exceeded while preserving active reasoning. The headline run is a single session that completed 89 sequential tasks across 80 million tokens with no measurable accuracy loss relative to per-task isolated sessions. That is the difference between truncation, which forgets the wrong things, and eviction, which forgets the things it can prove are done.

This is the same conceptual move an OS makes when it stops treating RAM as a flat buffer and starts treating pages as objects with reference counts and a replacement policy. "Less Context, Better Agents" lands in the same place from the empirical side: its best configuration is pruning *plus* a compact summary, because pure pruning eliminates stale-state errors but introduces premature termination — the agent forgets it still had work to do. Eviction needs a small persistent index of intent, exactly like a working set needs metadata. Longer-horizon variants such as [AdMem](https://arxiv.org/abs/2606.06787) make the analogy explicit, pairing a short-term context stack with a scalable long-term store that consolidates and prunes on its own.

## The cache constraint is what makes it hard

If eviction were free, everyone would already do it. The reason naive pruning has quietly hurt teams is that it breaks the prompt prefix, and a broken prefix invalidates the KV cache. You delete 20K tokens of stale tool output to save money and eat a full cache miss on the next turn — the savings evaporate and latency spikes.

[TokenPilot](https://arxiv.org/abs/2606.17016) (June 15) is the first of these papers to treat that as the central problem rather than a footnote. It splits the job in two: ingestion-aware compaction stabilizes prompt prefixes so environmental noise doesn't mutate the cached region, and lifecycle-aware eviction offloads segments only on a conservative batch-turn schedule, once their residual utility expires. The payoff is 56–61% cost reduction in isolated mode and up to 87% in continuous mode, with competitive task performance — numbers you only get if eviction and caching are co-designed instead of fighting each other.

[Still](https://arxiv.org/abs/2606.07878) (June 5) pushes the same instinct one level down the stack, into the KV cache itself. A small per-layer Perceiver, trained once against a frozen base model, compacts keys and values in a single forward pass at compression ratios from 8× to 200×, beating the strongest baseline by 8–22 points on RULER and remaining reusable across a trajectory. Read together, the two papers describe a two-tier memory manager: token-level eviction governs *what the model sees*, and KV-level compaction governs *what the GPU holds*. They are different layers of the same hierarchy, and you will want both.

## What this changes for builders

The practical takeaway is that "stuff the window and summarize when it's full" is now a known-bad default, not a reasonable starting point. If you are building long-horizon agents, three things follow.

Stop equating more context with more capability. Past a few recent turns, raw tool output is a liability — measure stale-state errors, not just token count. Make eviction deterministic where you can; a typed-episode policy is debuggable and free, while a summarization call is neither. And design eviction and caching together — an eviction scheme that ignores prefix stability will cost you more than the context it removes. The discipline we called context engineering is hardening into a system component with the same primitives as virtual memory: a working set, a replacement policy, and a cache you are not allowed to thrash. The teams that internalize that this quarter will ship agents that run longer, cost less, and — counterintuitively — think more clearly.

## Worth bookmarking

- [Less Context, Better Agents](https://arxiv.org/abs/2606.10209) — the empirical case that pruning beats full history on accuracy and cost.
- [Beyond Compaction: Structured Context Eviction](https://arxiv.org/abs/2606.11213) — deterministic, LLM-free eviction over typed episodes; 89 tasks across 80M tokens.
- [TokenPilot](https://arxiv.org/abs/2606.17016) — cache-aware eviction that co-designs prefix stability with offloading.
- [Still: Amortized KV Cache Compaction](https://arxiv.org/abs/2606.07878) — single-forward-pass KV compaction at 8×–200×.
- [AdMem](https://arxiv.org/abs/2606.06787) — bi-level memory with a short-term context stack and a self-pruning long-term store.
- [MemRefine](https://arxiv.org/abs/2606.13177) — LLM-guided compression for long-term agent memory.
