---
title: "Where the Reward Goes: Agent RL's Reward-Design Split"
description: "Recent papers disagree on whether to reward agents per-turn or only at the end — and the answer reveals where RL for agents is actually headed."
pubDatetime: 2026-05-29T11:00:00-07:00
tags:
  - agents
  - rl
  - reward-design
  - multi-agent
  - reasoning
featured: false
draft: false
---

If you train an LLM agent with reinforcement learning, the single most consequential decision you make is not the algorithm, the base model, or the rollout budget. It's where you put the reward. The last two weeks of research make this uncomfortably clear: serious groups are publishing results that point in opposite directions, and the disagreement is not noise. It's a map of where agent RL is genuinely unsolved.

## The reward-shaping contradiction

Start with the contradiction, because it is sharp. One line of work argues you should reward agents at every turn. ["Reinforcing Multi-Turn Reasoning in LLM Agents via Turn-Level Reward Design"](https://arxiv.org/pdf/2505.11821) makes the credit-assignment case directly: in a long tool-use trajectory, an outcome-only signal tells the model that *something* in twelve steps worked, but not *what*. By scoring intermediate turns, the agent learns which reasoning steps and tool calls actually advanced the task. The paper reports gains across multi-step QA, tool use, and math against outcome-only baselines.

Now read it next to ["An Empirical Study on Reinforcement Learning for Reasoning-Search Interleaved LLM Agents"](https://arxiv.org/pdf/2505.15117) from Bowen Jin and collaborators, which finds nearly the reverse: for agents that interleave reasoning with search, **outcome-based rewards beat dense intermediate rewards**, and sparse signals outperform shaped ones. Trying to reward every "good" search decision degraded the agent. That is a direct shot at the conventional RL instinct to shape rewards throughout the trajectory.

These are not actually in conflict once you look at *what* is being rewarded per turn. The turn-level reward work succeeds when the intermediate signal is **verifiable** — a turn either produced a correct sub-result or it didn't. The interleaved-search study fails when the intermediate signal is **heuristic** — a human guess about what good search behavior looks like. The lesson that survives both papers: dense rewards help only when each step has ground truth. The moment you start hand-shaping rewards to encode your intuitions about good process, you are teaching the model to game your intuitions. Outcome rewards, for all their sparsity, at least cannot be hacked into rewarding the wrong thing.

If you are building an agent RL pipeline today, this is the practical takeaway. Before adding turn-level rewards, ask whether you can *check* each turn, not whether you can *score* it. If you can only score it, you probably want the sparse outcome signal instead.

## The reward target is moving up the stack

The more interesting shift is *what* the RL is optimizing. Most agent RL still trains a single policy to reason and call tools better. But the multi-agent world has a different object to optimize: the orchestration itself. Chenchen Zhang's survey ["Reinforcement Learning for LLM-based Multi-Agent Systems through Orchestration Traces"](https://arxiv.org/html/2605.02801v1) is the cleanest framing of this I've seen. It decomposes orchestration into five learnable decisions — when to spawn a sub-agent, whom to delegate to, how to communicate, how to aggregate results, and when to stop — and argues you should train on *orchestration traces* (a temporal event graph of spawns, delegations, returns, and aggregations) rather than on individual agent trajectories.

The buried lede is the fifth decision. As of early May 2026, the survey found **no explicit RL method that trains the stopping decision**. Every production multi-agent system today decides when a task is done using a hand-written heuristic or a prompt instruction — exactly the kind of un-trained, un-verified policy that the reward-design papers above warn against. If you have watched a multi-agent run burn tokens because no sub-agent would declare victory, you have seen this gap in the wild. It is the most concrete open problem in the area right now, and it is wide open for anyone with an environment and a reward function.

## The substrate is finally here

What makes both threads more than academic is that the tooling to act on them shipped this spring. [Agent-R1](https://github.com/AgentR1/Agent-R1) (v0.1.0, March 2026) models agent interactions as **step-level MDP transitions** — each step records its observation, action, environment feedback, reward, and termination state as an explicit unit, instead of flattening everything into one growing prompt-response blob. That representation is precisely what you need to attach turn-level rewards cleanly, and to assign credit to orchestration decisions. It supports GRPO, PPO, REINFORCE++, and RLOO out of the box, with GRPO coming out strongest across their benchmarks — consistent with the broader trend toward critic-free, group-normalized methods because they are cheaper to run and easier to reason about.

Put the three pieces together and a coherent picture emerges. The field is converging on **verifiable, step-boundaried environments** as the foundation, GRPO-family algorithms as the default optimizer, and a slow migration of the reward target from the individual agent up to the orchestrator. The reward-shaping debate isn't a debate about technique; it's the field discovering that you can only reward what you can verify, and that most of what we want agents to do well — knowing when to stop, when to delegate, when to quit searching — we have not yet figured out how to verify.

That is the real frontier. Not a better algorithm. A better definition of "done."

## Worth bookmarking

- [Turn-Level Reward Design for Multi-Turn Reasoning](https://arxiv.org/pdf/2505.11821) — the case for verifiable per-turn rewards.
- [RL for Reasoning-Search Interleaved Agents](https://arxiv.org/pdf/2505.15117) — the counter-case: sparse outcome rewards win when steps aren't checkable.
- [RL for Multi-Agent Systems via Orchestration Traces](https://arxiv.org/html/2605.02801v1) — the five orchestration decisions and the unsolved "when to stop."
- [Agent-R1](https://github.com/AgentR1/Agent-R1) — step-level MDP framework for end-to-end agent RL (GRPO/PPO/RLOO).
- [VoltAgent/awesome-ai-agent-papers](https://github.com/VoltAgent/awesome-ai-agent-papers) — a maintained 2026 index of agent research across RL, memory, and evaluation.
