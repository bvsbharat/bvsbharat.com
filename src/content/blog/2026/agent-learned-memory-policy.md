---
title: "Agents Are Learning the Memory Policy You Used to Hand-Code"
description: "A June 2026 wave moves the store/evict/retrieve decision from heuristics to a trained policy, and pushes consolidation into an offline sleep phase."
pubDatetime: 2026-06-21T11:00:00-07:00
tags:
  - agents
  - memory
  - rl
  - skills
  - self-improvement
featured: false
draft: false
---

The interesting shift in agent memory this month is not that agents got more of it. It is *who decides what to keep*. For two years that decision lived in your code: a retrieval threshold you tuned, a summarize-every-N-turns rule, a hand-written eviction heuristic. A cluster of work landing through June 2026 takes that decision away from you and hands it to a trained policy — and moves the expensive part of it off the inference path entirely, into something that looks a lot like sleep.

This cuts against the grain of the recent consensus. The argument that short-term context eviction should be *deterministic and LLM-free* is well made and, for the working set, correct. But that's the within-session story. The cross-session story — what an agent carries from yesterday's tasks into today's — is going the opposite direction. There, the management logic is becoming the thing you train.

## The store/evict decision is becoming a policy, not a rule

The clearest statement of this is [Agentic Memory (AgeMem)](https://arxiv.org/abs/2601.01885), which stops treating store, retrieve, update, summarize, and discard as plumbing the framework calls on the agent's behalf. It exposes all five as tools the agent can invoke, then optimizes the whole pipeline with reinforcement learning — a supervised warm-up, then outcome-level RL, then a step-wise GRPO variant that hands out denser credit for individual memory actions instead of waiting for the task to end. The point is the credit assignment: "should I have kept that observation" becomes a learnable decision with its own reward signal, not a constant in a config file. It buys 4.8 to 8.6 points of average task performance over memory-augmented baselines, but the number matters less than the move.

[ALMA](https://arxiv.org/abs/2602.07755) pushes one level of abstraction higher and asks a meta-agent to *design the memory system itself*, writing candidate designs as executable Python, scoring them, and keeping an archive of partial successes as stepping stones rather than greedily chasing the current best. Its learned designs beat human-crafted baselines by 6 to 13 percent across ALFWorld, TextWorld, Baba Is AI, and MiniHack. Read AgeMem and ALMA together and the trajectory is obvious: first the memory operations get trained, then the architecture that arranges them does too. The hand-tuned retrieval threshold is on the same path the hand-tuned learning rate took a decade ago.

## Consolidation is moving to an offline phase

The second move is about *when* improvement happens. If the management logic is learned and the lessons are mined from experience, you don't want any of that on the hot path while a user waits. So it's migrating into a background job.

Microsoft's [SkillOpt](https://github.com/microsoft/SkillOpt) treats a skill — a 300-to-2,000-token markdown file — as the trainable artifact, running a rollout → reflect → aggregate → select → update → evaluate loop that only commits a bounded text edit when it passes a validation gate. Weights never move; the deployed `best_skill.md` runs on a frozen model with zero extra calls. The release worth noting is the June 15 preview of *SkillOpt-Sleep*: a nightly companion that reviews past sessions, replays recurring tasks, and consolidates the skills that held up. That's not a metaphor I'm reaching for — it is explicitly a sleep cycle, a separate consolidation pass that runs when nobody is watching.

The research side arrives at the same structure from experience rather than skills. [Trajectory-Informed Memory Generation](https://arxiv.org/abs/2603.10600) parses finished trajectories into strategy tips from wins, recovery tips from failures, and optimization tips from the slow-but-correct runs — each carrying provenance back to the trajectory that produced it — then retrieves them by task similarity, lifting held-out completion by up to 14 points and far more on the hardest tasks. [XSkill](https://arxiv.org/abs/2603.12056), at ICML 2026, splits the same idea cleanly: task-level *skills* (reusable workflows and tool templates) and action-level *experiences* (tactical insights), both distilled from rollouts with no parametric training, then injected at inference. The common shape across all of these is a two-phase system — act, then later consolidate — which is the oldest idea in learning systems wearing new clothes.

## What this changes for builders

If you ship agents, you now own a second training loop, and you own it without a GPU budget. That's the upside and the trap.

The upside: you can close a real self-improvement loop in text, validate every change before it lands, and roll it back by reverting a file. The trap is that a learned consolidation phase will faithfully learn the wrong lesson if your reward is noisy — it will canonize a lucky path or a coincidence and serve it back as advice, and because it lives in retrieved text rather than weights, it can look like a prompt bug for weeks. So three things follow. Keep provenance on every consolidated memory, the way Trajectory-Informed Memory does, so a bad lesson is traceable to the run that taught it. Gate every write behind a validation step, the way SkillOpt does, and treat an unvalidated edit as a regression rather than an improvement. And keep the two timescales separate: deterministic, LLM-free eviction for the within-session working set, a trained-and-audited policy for the cross-session store. They are different problems, and conflating them is how you get an agent that is both forgetful in the moment and confidently wrong over the long run.

The hand-written memory heuristic had a good run. The next version of it is going to be trained, run in the background, and checked in as a file you can read.

## Worth bookmarking

- [Agentic Memory (AgeMem)](https://arxiv.org/abs/2601.01885) — memory operations as RL-trained tools in the agent's own policy.
- [ALMA: meta-learning agentic memory designs](https://arxiv.org/abs/2602.07755) — a meta-agent that writes and scores memory architectures as code.
- [SkillOpt](https://github.com/microsoft/SkillOpt) — text-space skill optimization for frozen models, now with an offline "Sleep" consolidation preview.
- [Trajectory-Informed Memory Generation](https://arxiv.org/abs/2603.10600) — provenance-tagged learnings mined from finished trajectories.
- [XSkill](https://arxiv.org/abs/2603.12056) — skills versus experiences, distilled from rollouts without parametric training (ICML 2026).
