---
title: "Code with Claude 2026: Five Things That Actually Matter"
description: "Anthropic shipped a lot on May 6 — Managed Agents updates, Dreaming, Outcomes, Multi-agent Orchestration, and a SpaceX partnership. The signal-to-noise filtered down to five things that change how you build."
pubDatetime: 2026-05-07T08:00:00-07:00
tags:
  - agent-tools
  - anthropic
  - claude
  - agents
  - managed-agents
  - announcements
featured: false
draft: false
---

[Code with Claude 2026](https://www.infoq.com/news/2026/05/code-with-claude/) ran in San Francisco yesterday. Anthropic shipped enough that you could write 12 blog posts about it; most of those blog posts have already been written, mostly by people who hadn't tried any of it yet. This post is the opposite: five things from the day that actually change how you build agents, with the rest filed under "interesting but downstream."

If you're using Claude for production agent work, the five items below are the ones to plan around. If you're not, the first three are still the most important shifts in the platform agent space this year.

## 1. Dreaming, in research preview

The headline announcement, and the one I've been most curious about since the rumors started in April. [Dreaming](https://letsdatascience.com/blog/anthropic-dreaming-claude-managed-agents-self-improving-may-6) is a background process for Claude Managed Agents: between jobs, the agent reviews its own session traces and memory store, identifies recurring patterns and mistakes, and updates the memory entries.

The mechanics, as described in the keynote and the technical doc:

- Runs during idle periods on the agent's compute allocation
- Reads session traces, the existing memory store, and tagged outcomes
- Produces three kinds of edits: condense (merge redundant entries), promote (mark a memory as load-bearing), and deprecate (flag stale or contradicted entries)
- Does not modify model weights — only the memory store
- Configurable: per-agent toggle, per-session opt-out, hard time/cost cap

The Harvey case study that closed the demo segment cited a 6x lift in task completion across their internal agent population. I covered the broader memory-as-infrastructure story in [last week's post](/blog/agent-memory-becomes-infrastructure); Dreaming is the productized version of the offline-reflection primitive multiple research labs have been chasing for the last year.

What's actually news here: this is the first time a frontier lab has shipped a structured "improve overnight" loop as a product. The mechanism is conservative — no weight updates, no opaque training — but the result is an agent that gets better at your codebase over time without you doing anything. That's the same compounding advantage humans get on day five vs. day one of a new job, and the field's been waiting for a credible way to give agents a version of it.

What's not yet clear: how well Dreaming works for narrow agents with little session diversity, what happens when the memory store hits scale limits, and whether the "structured note-taking" framing survives adversarial inputs (a malicious user trying to inject false memories). The research preview is honest about all three.

## 2. Outcomes goes public beta

The second important primitive: [Outcomes](https://www.testingcatalog.com/anthropic-launches-new-secure-tools-for-claude-managed-agents/) is a self-grading loop where a separate evaluator scores an agent's output against a written rubric and either approves or tells the agent what to fix.

This is the critic role from the [planner-executor-critic pattern](/blog/deep-agents-planner-executor-critic) blessed by the platform. The structure:

- You write a rubric (specific checks, not a 1-10 score)
- The evaluator runs after the agent produces output
- Pass/fail per rubric item, plus reasons
- Failed items go back to the agent as feedback
- Hard retry limit; escalation path on persistent failure

The thing that makes Outcomes useful — and not just "another LLM-as-judge" — is the structure. The rubric isn't a vibe; it's a checklist. The evaluator isn't asked "is this good"; it's asked "does this satisfy these specific checks." Different model than the worker, so the blind spots don't align.

For teams that have been hand-rolling critic loops, Outcomes saves you the integration work. For teams that haven't been running critics, this is the lowest-friction way to add one. Either way, public beta means it's ready for real workloads, not just demos.

## 3. Multi-agent Orchestration, public beta

The third pillar of the Managed Agents update: [multi-agent orchestration](https://9to5mac.com/2026/05/07/anthropic-updates-claude-managed-agents-with-three-new-features/) — a Lead agent can break a job into pieces and delegate each one to a specialist with its own model, prompt, and tools. Specialists return structured results to the Lead.

Three things I want to flag:

**Depth-1 by design.** The Lead can dispatch to specialists; specialists cannot dispatch to other specialists. This is the same constraint Anthropic put on the [skills/connectors/subagents](/blog/skills-connectors-subagents-template) template format. It's a real architectural choice — depth-1 keeps the call graph predictable, the tool surface in the Lead's context bounded, and debugging tractable. Deeper trees were possible and the team explicitly chose not to.

**Per-specialist model choice.** Every specialist picks its own model. The Lead might be Opus 4.7; one specialist is Sonnet 4.6; another is Haiku 4.5. This is the per-task model selection win from [cost-optimized agent architectures](/blog/cost-optimized-agent-architectures) made into a first-class platform feature. The implementation is exactly what teams have been rolling by hand, now bundled.

**Parallel dispatch.** A Lead can dispatch multiple specialists simultaneously. Wall-clock latency drops accordingly. Cost stays at the sum-of-parts.

If you've been building sub-agent systems by hand, Multi-agent Orchestration is the platform version of what you built. Worth migrating to if your existing setup wasn't already wired up to Anthropic's tracing and outcomes infrastructure.

## 4. Secure sandboxes and private MCP servers

The infrastructure layer of the announcement got less stage time and more practical importance. [Secure sandboxes](https://www.testingcatalog.com/anthropic-launches-new-secure-tools-for-claude-managed-agents/) and private MCP servers shipped at the same time, and together they close a real gap in the platform story.

**Secure sandboxes** are first-party sandboxed execution environments for Managed Agents. The agent can write and run code, the code runs in an isolated environment, you don't have to wire E2B or Modal yourself. The isolation primitive is Firecracker microVM. Cost is bundled with the agent's compute allocation. Cold start is 200-400ms, in line with industry expectations.

**Private MCP servers** let you run an MCP server that's accessible only to your Managed Agents — no public endpoint, no shared infrastructure, governed by IAM-style permissions. The architectural value: you can put your internal data behind an MCP server without exposing it to the world. The integration value: it's just an MCP server, so the same code works on your laptop and in the managed environment.

Together, these turn Managed Agents into a credible "all-batteries-included" platform for enterprise agent deployment. The story before this was "Anthropic for the model, E2B for sandbox, Cloudflare/AWS for MCP hosting, separate billing, separate identity." Now it's one platform. The integration cost of building agents on the platform drops materially.

The trade-off: lock-in is real. If you build on Managed Agents + Secure Sandboxes + Private MCPs, switching to a different runtime is significant work. That trade-off is the same one every cloud has demanded for two decades, and the customers willing to make it generally come out ahead on time-to-deploy. Worth thinking through whether it's the right call for your use case.

## 5. SpaceX Colossus partnership for compute

The closing announcement: Anthropic is [partnering with SpaceX](https://www.infoq.com/news/2026/05/code-with-claude/) to use all of the capacity of the Colossus data center. The compute story behind the Managed Agents push has been pressed against the ceiling for months — every team I work with has had to budget for capacity throttling at peak — and Colossus is the part that buys headroom.

Two practical implications for builders:

**Five-hour limits doubled** for Pro, Max, and Enterprise customers. The previous limit was the single biggest complaint from Claude Code power users. Doubling it doesn't make it infinite, but it makes long-running coding sessions much less fraught.

**Capacity-based throttling should ease over the next quarter.** Anthropic was careful not to promise specific numbers, but the Colossus partnership is the long-term answer to "we're sometimes capacity-constrained." Pricing isn't expected to drop in the near term; availability should improve.

The SpaceX angle gets the headlines. The capacity expansion is what actually matters for production deployments.

## What didn't change

For honesty, the things that I expected to move and didn't:

**Claude Code subagent depth.** Still depth-1. There's no path to nested subagents in this release.

**MCP-on-Claude-Code parity with Claude Cowork.** Subtle differences in MCP server lifecycle between Claude Code and Cowork remain. Not addressed in this release; presumably the next one.

**A formal Anthropic Skills marketplace.** The [skills/connectors/subagents template format](/blog/skills-connectors-subagents-template) has been the de facto standard since May 5, but Anthropic didn't ship a marketplace for third-party skill publication. The cookbook is the substitute. A real marketplace remains a 2026 H2 item at best.

**A consumer agent product.** No "Claude Operator." The agent story remains developer-platform-shaped, not consumer-shaped. Whether that changes before the end of the year is the open question.

## What this means for the next quarter

Three concrete moves if you're shipping on Claude:

1. **Migrate hand-rolled sub-agent systems to Multi-agent Orchestration.** If your existing wiring works and you're getting decent tracing, you can wait. If you're patching the rough edges of a homegrown setup, the platform version is now production-ready and saves you maintenance.
2. **Add Outcomes to any agent that produces consequential output.** Critic loops are cheap to add now and catch a category of bugs you can't catch any other way. Public beta means it's stable enough.
3. **Try Dreaming on agents that handle repeated workflows.** Research preview means feedback channel is open. The agents that benefit most are the ones that see the same kind of task many times — coding agents, support agents, ops agents.

The honest summary: Code with Claude 2026 was the most product-shipping-heavy keynote I've seen from any frontier lab. The pace of change in the agent platform layer is now the rate-limiting factor on what teams can ship, not the model itself. That's a meaningful change in the texture of this work. The teams that pay attention to the platform layer — and not just the model leaderboards — are the ones who'll have the most leverage over the next two quarters.

## Worth bookmarking

- [InfoQ recap of Code with Claude 2026](https://www.infoq.com/news/2026/05/code-with-claude/) — comprehensive event summary
- [Simon Willison's live blog](https://simonwillison.net/2026/May/6/code-w-claude-2026/) — running commentary from the keynote
- [Anthropic Dreaming deep dive](https://letsdatascience.com/blog/anthropic-dreaming-claude-managed-agents-self-improving-may-6) — mechanism explained
- [Testing Catalog: secure sandboxes and private MCPs](https://www.testingcatalog.com/anthropic-launches-new-secure-tools-for-claude-managed-agents/) — infrastructure announcement details
- [9to5Mac on the three Managed Agents features](https://9to5mac.com/2026/05/07/anthropic-updates-claude-managed-agents-with-three-new-features/) — product-side summary
- [Dotzlaw analysis of doubled limits and infinite context](https://www.dotzlaw.com/insights/anthropic-2026-code-with-claude/) — what the capacity changes mean for production teams
