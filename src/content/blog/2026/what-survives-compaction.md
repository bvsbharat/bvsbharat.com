---
title: "What Survives Compaction Is the Real Context Window"
description: "June's research reframes context management: the discard step is now where both agent quality and safety quietly leak."
pubDatetime: 2026-07-01T11:00:00-07:00
tags:
  - agents
  - context-engineering
  - agent-safety
  - long-horizon
featured: false
draft: false
---

For most of the past two years, "context" was a capacity question: how many tokens can I fit, how much do they cost, how far back can the model actually attend. The interesting engineering happened on the way *in* — retrieval, packing, tool-result trimming. A cluster of June research flips the frame. On long-horizon runs the model doesn't hit a wall because the window is too small; it hits a wall because *something got thrown away* at a bad moment, or the wrong thing got thrown away entirely. Compaction — the summarize-and-discard step every long-running agent now performs — has quietly become the place where both correctness and safety leak. The real context window isn't what you can hold. It's what survives the discard.

Three papers this month attack that discard step from different directions, and read together they say the same thing: compaction is a decision, and right now most agents make it badly.

## Timing: a token counter is the wrong trigger

The default compaction trigger is a threshold — the buffer crosses some percentage of the window, so you summarize. [Self-Compacting Language Model Agents](https://arxiv.org/abs/2606.23525) (Li et al.) makes the obvious-in-hindsight point that a token counter can't tell whether the trajectory just cleanly closed a sub-task or is three steps into a five-step derivation. Compaction at the first is free; at the second it destroys the working state the model is about to need, forcing expensive re-derivation.

Their fix, SelfCompact, hands the model a compaction tool plus a rubric for *when* to fire it (a sub-task resolved, the trajectory is converging) and when to hold (mid-derivation, or stuck). Letting the model choose the moment matched or beat fixed-interval summarization at a fraction of the cost — up to 18.1 points on math, 5–9 on agentic search, at 30–70% lower token cost, across seven models with no fine-tuning. Blake Crosley framed the same idea crisply in a [June essay](https://blakecrosley.com/blog/agent-context-compaction): "context compaction is a decision, not a threshold." Semantic timing beats numeric timing because the numeric trigger is blind to the one thing that matters — where the agent is in its own reasoning.

## Contents: dropping the wrong thing is a safety hole

The scarier result is about *what* gets dropped. [Governance Decay](https://arxiv.org/abs/2606.22528) (Shiyang Chen) studies what happens to in-context safety constraints — the "never touch production," "don't email customers," "no financial transactions" rules that live in the system prompt — when they scroll far enough back to get compacted away. The finding is stark: across 1,323 episodes, policy violations jumped from 0% under full context to 30% after compaction, and as high as 59% on some models. When a constraint survived the summary, violations stayed at 0%; when it got dropped, they hit 38%.

That is a genuinely new failure mode. The constraint isn't jailbroken, argued away, or overridden. It's simply *forgotten* — silently omitted by a summarizer that treated a safety rule as low-salience boilerplate compared to the live task chatter. And because summarizers can be steered, Chen also demonstrates a Compaction-Eviction Attack: adversarial content injected earlier in the trajectory biases the summarizer into dropping legitimate policies on its next pass. Every model evaluated was vulnerable. The mitigation, Constraint Pinning, is unglamorous and effective — exempt governance rules from lossy compression so they're re-emitted verbatim into every compacted context — and it restored violations to 0%. The lesson generalizes past safety: any invariant your agent must honor for the whole run cannot be left to the summarizer's discretion.

## Budget: curation under a fixed ceiling

The third thread treats the whole thing as a budgeting problem. [ContextBudget](https://arxiv.org/pdf/2604.01664) (Wu et al.) frames long-horizon search as active curation under a token ceiling — the agent decides which accumulated results are load-bearing for continuing and which can be released — and shows that thoughtful curation extends reasoning chains without sacrificing solution quality, versus passively hitting the limit. Related work on adaptive parallel context routing for long-horizon web agents points the same way: which context an agent keeps in front of it is a policy worth optimizing, not a side effect of a ring buffer.

## The summarizer is now a load-bearing component

Put the three together and the takeaway is a mindset shift. The summarizer that produces your compacted context has quietly become one of the most consequential components in the stack, and most teams treat it as plumbing — a fixed prompt, fired on a token threshold, output never inspected. That's untenable if dropping a line can flip a safety constraint or delete a half-finished proof.

Concretely, if you run long-horizon agents:

- **Pin your invariants.** Safety rules, task constraints, and identity/scope facts should be re-injected verbatim after every compaction, never summarized. Cheap, and it closes the Governance Decay hole.
- **Trigger on state, not size.** Prefer compacting at sub-task boundaries over token thresholds. If you can't do model-driven timing yet, at least avoid compacting mid-derivation.
- **Log what you dropped.** Diff the pre- and post-compaction context and keep the delta. When a long run goes wrong, "what did the summarizer delete three steps back" is often the answer, and today it's usually unrecoverable.
- **Treat the summarizer as attack surface.** If earlier turns can contain untrusted content, assume an adversary can bias what gets evicted, and pin accordingly.

For a year the context conversation was about the size of the window. The more useful question now is narrower and harder: of everything this agent has seen, what does it actually need to keep — and are you sure that's what survived the last compaction?

## Worth bookmarking

- [Self-Compacting Language Model Agents](https://arxiv.org/abs/2606.23525) — model-driven compaction timing; matches fixed-interval quality at 30–70% lower cost.
- [Governance Decay](https://arxiv.org/abs/2606.22528) — compaction silently erases safety constraints; introduces Constraint Pinning and the Compaction-Eviction Attack.
- [ContextBudget](https://arxiv.org/pdf/2604.01664) — long-horizon search as active context curation under a token budget.
- [Context Compaction Is a Decision, Not a Threshold](https://blakecrosley.com/blog/agent-context-compaction) — the argument for semantic over numeric triggers.
- [Claude context-engineering cookbook](https://platform.claude.com/cookbook/tool-use-context-engineering-context-engineering-tools) — practical memory, compaction, and tool-clearing patterns.
