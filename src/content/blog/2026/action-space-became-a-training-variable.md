---
title: "The Agent's Action Space Became a Training Variable"
description: "June 2026 research stopped treating an agent's skills and tools as a fixed library and started co-optimizing them with the policy via RL."
pubDatetime: 2026-07-02T11:00:00-07:00
tags:
  - agents
  - reinforcement-learning
  - skills
  - tool-use
  - evals
featured: false
draft: false
---

For the last year the working assumption was that you make an agent better by giving it more: more tools, more skills, a bigger library of reusable procedures. A wave of papers from the last two weeks quietly retired that assumption. The new question is not "what capabilities do I hand the model" but "which parts of the action space actually earn their place once you optimize for returns" — and the answer, increasingly, is decided by reinforcement learning rather than by a human curating a folder of markdown files.

## The benchmark that started the argument

The uncomfortable data point is a few months old but still setting the terms of the debate. [SkillsBench](https://arxiv.org/html/2602.12670v1) evaluated 86 tasks across 11 domains under three conditions: no skills, human-curated skills, and skills the agent generated for itself. Curated skills helped a lot — plus 16.2 points on average, though with high variance. Skills the agent wrote for itself moved the needle by *negative* 1.3 points. On average, letting the model author its own skills made it slightly worse.

The trajectory analysis explains why. Models correctly sense that a domain skill is needed but write vague procedures ("use pandas for data processing" with no API specifics), or on high-knowledge tasks fail to recognize that a specialized skill is called for at all. A companion result, [SkillGenBench](https://arxiv.org/pdf/2605.18693), makes the same point from the other side: generating a good skill is meaningfully harder than using one. That is a problem, because "the agent writes its own skills" was supposed to be the whole point of skill libraries.

## June's answer: put skill creation inside the RL loop

The response that landed in June is coherent enough to be called a school of thought. Instead of letting an agent freewrite skills at inference time and hoping they help, these systems fold skill creation into training and gate it on whether it raises verifiable returns.

[ReSkill](https://arxiv.org/abs/2606.01619) (from Amazon Science, with [code](https://github.com/amazon-science/reskill)) names the tension directly: skill abstraction can pull an agent *away* from reward-maximizing trajectories even as it improves reuse. Its fix is a veRL extension that co-evolves skills with the policy — an assertion-driven creator diagnoses failures from past rollouts and proposes conditional, trigger-based skill revisions, while within-group rollout sampling lets the trainer compare skill versions under controlled conditions. A skill only survives if the group that used it did better. [SkillSmith](https://arxiv.org/pdf/2606.01314) pushes the idea further, co-evolving skills *and* the tools they call in a bidirectional loop: skills expand as new tool uses are discovered, tools get refined by skill-driven demand. [SkillRevise](https://arxiv.org/pdf/2606.01139) conditions revisions on execution traces rather than the model's own theory of what went wrong, and [OpenSkill](https://arxiv.org/pdf/2606.06741) targets open-world self-evolution.

The through-line: credit assignment no longer stops at the trajectory. It now extends to the action space itself. The relevant question a trainer asks is not just "was this rollout good" but "did adding this abstraction make rollouts better" — and if the answer is no, the skill does not get to persist. That is a very different discipline from the inference-time skill-writing that SkillsBench measured, and it is the reason the same capability that scored -1.3pp raw can become useful once it is trained in.

## The other direction: fewer tools, not more

Running against the accumulation instinct is a minimalist result worth taking seriously. [RepoNavigator](https://arxiv.org/html/2512.20957) ("One Tool Is Enough," updated in late May) throws out the multi-tool pipeline for repository navigation and trains an agent, end-to-end with RL, around a single execution-grounded tool: `jump`, which resolves a symbol to its definition. The reasoning is mechanical. Every extra tool widens an action space full of interfaces the model never saw in pretraining, and chained tool calls compound failure — overall success is the product of per-tool success rates. Collapse the space to one tool aligned with execution semantics and both problems shrink.

The numbers are the argument. On SWE-bench Verified localization, RepoNavigator's 7B model beats 14B baselines, its 14B beats 32B competitors, and its 32B exceeds GPT-5 on most metrics — without distilling from a closed teacher. It is the same lesson as the skill work seen from the opposite end: the action space is something you optimize, and "optimize" sometimes means "delete," not "add." (For the maximalist tooling case, [VerlTool](https://arxiv.org/html/2509.01055v1) offers the holistic tool-RL counterweight — but note it too makes tools part of the training loop, not a static menu.)

## What this changes for builders

Three practical takeaways. First, do not ship self-generated skills straight to production; SkillsBench is a clear warning that inference-time skill authoring is unreliable, and the fixes all involve training or curation, not raw generation. Second, start measuring every skill and tool against returns, not against usage — a skill that gets invoked constantly but does not improve outcomes is dead weight the RL-in-the-loop systems would prune. Third, when a task has a clean execution-grounded primitive, try the minimal action space before the elaborate one; RepoNavigator suggests the ceiling on "one right tool, RL-trained" is higher than most multi-tool scaffolds reach.

The framing that ties it together: your agent's toolset stopped being an SDK you assemble and became a variable you optimize. Whoever owns that optimization loop — a trainer, a co-evolution scheduler, or a human with a benchmark — owns the agent's actual capability.

## Worth bookmarking

- [ReSkill: Reconciling Skill Creation with Policy Optimization in Agentic RL](https://arxiv.org/abs/2606.01619) — and its [code](https://github.com/amazon-science/reskill)
- [SkillSmith: Co-Evolving Skills and Tools for Self-Improving Agent Systems](https://arxiv.org/pdf/2606.01314)
- [SkillsBench](https://arxiv.org/html/2602.12670v1) — the benchmark showing self-generated skills underperform curated ones
- [RepoNavigator: One Tool Is Enough](https://arxiv.org/html/2512.20957) — RL with a single execution-grounded tool
- [SkillGenBench](https://arxiv.org/pdf/2605.18693) — why generating skills is harder than using them
