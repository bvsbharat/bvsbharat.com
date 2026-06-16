---
title: "Optimization Is Moving From Weights to English"
description: "Recent work turns skills, harnesses, and context into objects you can search over and benchmark — optimizing the English around a frozen model instead of the model."
pubDatetime: 2026-06-16T11:00:00-07:00
tags:
  - agents
  - skills
  - harness
  - optimization
  - context-engineering
featured: false
draft: false
---

For two years the default lever for "make the agent better" was the model: fine-tune it, RLHF it, run RL in an environment until the policy improves. A cluster of papers from the last few months quietly moves the lever somewhere else. The thing being optimized is no longer the weights — it's the English wrapped around the weights. The skills, the harness control flow, the context files, even the evaluation rig. These are now being treated as searchable, benchmarkable objects, and the search is being automated.

This is the natural next move after the harness got a name. Once you've isolated the scaffolding as a distinct layer, the obvious question is: can you optimize it the way you optimize a model? The answer, increasingly, is yes — and that changes what "context engineering" means.

## From craft to search

The clearest statement of this is [Meta Context Engineering via Agentic Skill Evolution](https://arxiv.org/abs/2601.21557) (ICML 2026). Their framing is a bi-level loop: a meta-agent evolves the *skills* that govern context engineering — executable instructions and code — while a base-agent runs those skills and optimizes the actual context as files. The interesting operator is "agentic crossover," an evolutionary step that synthesizes better skills by reasoning over past trajectories and their measured performance. The reported gains are 5.6–53.8% relative improvement over hand-built context-engineering methods, averaging ~17%.

Read that carefully: nobody touched the model. The improvement comes entirely from a search over the natural-language and code artifacts the model reads. Context engineering, which most teams still practice as a craft — tweak the system prompt, reorder the few-shot examples, prune the tool list — is being reframed as an optimization problem with a fitness function.

[Natural-Language Agent Harnesses](https://arxiv.org/html/2603.25723v1) pushes the same idea up a level. Instead of burying the plan→execute→verify→repair loop inside Python, the authors make the harness itself an *executable natural-language object* — explicit contracts, role boundaries, state semantics, failure taxonomies — and run it under an interpreter they call an Intelligent Harness Runtime. The payoff that matters here isn't the absolute SWE-bench number (74.4% on their slice); it's the ablation: letting the harness *self-evolve* added +4.8%, and a natural-language re-implementation of an existing code harness beat the original (47.2% vs 30.4%). When the control logic is English, the agent can rewrite its own control logic.

## The evaluator is now in the loop too

The unsettling part is what happens when you point this optimization at the measuring stick. [Meta-Harness: End-to-End Optimization of Model Harnesses](https://arxiv.org/abs/2603.28052) (from Khattab, Finn, and collaborators) does exactly that — it automatically optimizes the *evaluation* harness: test cases, metrics, assessment criteria, tuned end-to-end with meta-learning plus evolutionary search rather than hand-maintained.

That is genuinely useful — eval harnesses rot, and maintaining them by hand is miserable — but it should set off an alarm. If you optimize the policy's scaffolding against a benchmark, and you also optimize the benchmark, you have two coupled search processes that can quietly converge on each other. The number goes up; you've learned less than the number suggests. Anyone adopting these techniques needs a held-out evaluator that is *not* in the optimization loop, the same way you'd never tune on your test set. The papers report real gains, but the honest reader keeps one eye on overfitting to the harness.

The breadth of this shift is captured in [Externalization in LLM Agents](https://arxiv.org/abs/2604.08224), a survey that puts memory, skills, protocols, and harness engineering under one umbrella: the agent's capability increasingly lives *outside* the weights, in artifacts it reads, writes, and now optimizes. Once you accept that framing, "optimize the agent" stops meaning "train the model" and starts meaning "search the externalized layer."

## What practitioners actually ship

The research is running ahead of practice, but the practice is moving. [Superpowers](https://github.com/obra/superpowers) (obra, released June 12) is a hand-authored version of the same instinct: a library of composable skills plus a development methodology for coding agents — a deliberate, curated scaffolding rather than an evolved one. It's worth holding next to the MCE results, because it marks the gap. Today, good teams write their skills and harness rules by hand and they work. The papers suggest a near future where you write a *seed* set, define a fitness function, and let an evolutionary loop find scaffolding you wouldn't have written.

The pragmatic read for builders:

- Treat your skills, harness rules, and context layout as a versioned artifact with a benchmark attached, not as prose you tweak by feel. The moment you have a fitness number, you can search.
- Keep the optimization target and the evaluation target separate. If the same loop that improves your agent also improves your eval, your metrics are lying to you.
- The gains are real but task-dependent — NLAH's own ablations show individual modules helping unevenly across tasks. Don't expect a universal "best harness"; expect a search you re-run per domain.
- Hand-authored scaffolding (Superpowers-style) is still the right starting point. Auto-evolution is a multiplier on a good seed, not a substitute for one.

The deeper point is about where leverage now sits. Frozen frontier models are extremely capable and increasingly commoditized; the differentiated work is in the English-and-code layer around them — and that layer just became something you can compile, not just write.

## Worth bookmarking

- [Meta Context Engineering via Agentic Skill Evolution](https://arxiv.org/abs/2601.21557) — bi-level co-evolution of skills and context; the cleanest "optimize the English" result.
- [Natural-Language Agent Harnesses](https://arxiv.org/html/2603.25723v1) — the harness as a self-evolving, executable NL object.
- [Meta-Harness: End-to-End Optimization of Model Harnesses](https://arxiv.org/abs/2603.28052) — optimizing the evaluator; powerful and dangerous in equal measure.
- [Externalization in LLM Agents](https://arxiv.org/abs/2604.08224) — the survey that unifies memory, skills, protocols, and harness under one frame.
- [Superpowers](https://github.com/obra/superpowers) — a shipping, hand-authored skills framework to anchor the research against.
