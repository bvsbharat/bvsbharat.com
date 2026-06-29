---
title: "Ten Agents, Three Merges: June's Tooling Fixed Fan-Out, Not Review"
description: "This month's agent tools made spawning parallel coding agents trivial. The constraint moved to the merge decision—and that doesn't parallelize."
pubDatetime: 2026-06-29T11:00:00-07:00
tags:
  - agents
  - orchestration
  - code-review
  - developer-tools
featured: false
draft: false
---

The cheapest thing in software this month is a coding agent doing work. The most expensive is a human deciding whether to trust the result. Every tool that shipped in June widened the first gap and ignored the second, and the bill is now visible in the benchmarks. You can fan one prompt across ten agents before your coffee is ready. You will still only merge three of those branches today, because the bottleneck stopped being generation and became adjudication—and adjudication has no parallel form.

That inversion is the actual story behind the June tooling wave, and it changes where the interesting engineering is.

## The control surface left the editor

The clearest signal is that the unit of interaction is no longer a chat pane inside an IDE. It's a queue of agents you supervise. [Orca](https://github.com/stablyai/orca)—an "agent development environment for running fleets of parallel coding agents," at v1.4.104 as of June 28—lets you "fan one prompt across five agents, each in its own isolated git worktree," then compare and merge the survivors. It drives Claude Code, Codex, Cursor, Grok, and 30-plus other CLI agents indiscriminately; the agent is now a swappable backend, and the product is the orchestration shell around it.

Google made the same bet at a different altitude. [Antigravity 2.0](https://www.agentupdate.ai/blog/google-antigravity-2-0-explained/) reframes the developer "from a toiling programmer to a team-leading project manager": a primary agent decomposes work and dispatches frontend, backend, and test subagents with independent context windows, while you watch through scheduled tasks, approval hooks on risky operations, and an inbox where the bots post progress. The migration off the old Gemini CLI was forced on June 18—Google is not treating the agent-manager surface as optional.

The enabling primitive underneath both is unglamorous: the git worktree. Isolate each agent in its own checkout and parallelism becomes a non-event—no shared mutable state, no clobbering, trivially many concurrent agents. That's why [ComposioHQ/agent-orchestrator](https://github.com/ComposioHQ/agent-orchestrator) (v0.10.1, June 29) and the [trending repos of late June](https://startupcorners.com/digest/devtools-digest-2026-06-25)—deer-flow, gstack—all converge on the same shape. Fan-out is solved. It's a worktree and a process per agent.

## Merge is the constraint, and it's getting worse

Solving generation just relocated the queue. [LinearB's 2026 benchmarks](https://linearb.io/dev-interrupted/podcast/linearb-2026-benchmarks-ai-pr-merge-rate) put numbers on it: agentic-AI pull requests have a pickup time **5.3x longer** than unassisted ones, AI-assisted PRs merge at **less than half the rate** of human-authored code, and median review duration is up over 400%. CircleCI's data shows feature-branch throughput up 59% year over year while median *main-branch* throughput actually fell. The work moved downstream and piled up against a wall.

The wall is a human making a trust decision, and two things make it slower per-PR than it used to be. First, the reviewer gets a finished diff with no implementation journey—no commit-by-commit trail of what the agent tried and abandoned—so intent has to be reconstructed from the ticket and the code alone. Second, agent code is plausible. It reads as correct on a casual pass, which makes review *harder*, not easier, because the cheap heuristic—"does this look like someone who knew what they were doing wrote it"—now returns a false positive every time.

This is why running ten agents overnight is often negative work. Three get reviewed in the morning; the other seven sit as branches that go stale, accumulate conflicts, and consume review attention later at a worse exchange rate. Parallel generation against serial review doesn't add throughput. It builds inventory.

## The honest responses, and the dishonest one

There are two coherent reactions to this, and the tools are starting to split along them.

The dishonest one is to declare the bottleneck obsolete. Martin Monperrus's June 11 paper, provocatively titled [*The End of Code Review*](https://arxiv.org/abs/2606.13175), argues that agents can already meet every stated goal of human review "at lower cost and higher throughput," and that keeping humans as mandatory reviewers "neither provides meaningful assurance nor scales." The diagnosis of the scaling problem is exactly right. The prescription—delete the checkpoint—is a leap the empirical record doesn't support yet, and notably the argument is asserted rather than measured.

The honest response is to make the loop close *before* it reaches you. The most interesting thing in agent-orchestrator isn't that it spawns agents—everything spawns agents now—it's that it routes CI failures, merge conflicts, and review comments back to the owning agent automatically. The agent fixes its own red build and reconciles its own conflict; the human sees a branch that's already green and rebased. That's the right move: don't try to parallelize the trust decision, *reduce the number of trust decisions that reach a human and raise the evidence attached to each one.*

The strategic line for the second half of 2026 follows directly. Fan-out is a commodity—stop optimizing it. The leverage is in everything between an agent finishing and a human deciding: self-verifying agents that arrive with tests and a refutation attempt already run, diffs that carry their implementation journey, and orchestrators that merge nothing until the evidence clears a bar. Spawning is free. Earning a merge is the product.

## Worth bookmarking

- [stablyai/orca](https://github.com/stablyai/orca) — open-source ADE for fleets of parallel agents, worktree-isolated, agent-agnostic.
- [ComposioHQ/agent-orchestrator](https://github.com/ComposioHQ/agent-orchestrator) — supervises parallel agents and auto-routes CI failures, conflicts, and review comments back to them.
- [Antigravity 2.0 explainer](https://www.agentupdate.ai/blog/google-antigravity-2-0-explained/) — Google's developer-as-manager surface with subagents, hooks, and an agent inbox.
- [LinearB 2026 benchmarks](https://linearb.io/dev-interrupted/podcast/linearb-2026-benchmarks-ai-pr-merge-rate) — the merge-rate and review-duration data behind the bottleneck.
- [*The End of Code Review*](https://arxiv.org/abs/2606.13175) (Monperrus, June 2026) — the maximalist case for retiring human inspection; read it to disagree well.
- [DevTools trending digest, June 25](https://startupcorners.com/digest/devtools-digest-2026-06-25) — snapshot of where the open-source agent-tooling energy is going.
