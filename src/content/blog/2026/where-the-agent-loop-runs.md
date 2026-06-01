---
title: "Where the Agent Loop Runs: The Control-Plane Split of May 2026"
description: "The week of May 19 separated the agent loop from tool execution. Whoever hosts the loop now owns your latency, reliability, and lock-in."
pubDatetime: 2026-06-01T11:00:00-07:00
tags:
  - agents
  - infrastructure
  - anthropic
  - mcp
  - runtime
featured: false
draft: false
---

For two years the interesting question about an agent was "which model?" The week of May 19, 2026 quietly replaced it with a harder one: **where does the loop run?** Anthropic, Google, and the serving-systems researchers all answered in the same seven days, and they did not agree. The agent loop — orchestration, context management, compaction, error recovery — is becoming a hosted service that can be separated from the tools it calls. That separation is now the most consequential architecture decision you make, and most teams haven't noticed they're making it.

## The loop and the tools came apart

The clearest signal was [Anthropic's self-hosted sandboxes and MCP tunnels](https://the-decoder.com/anthropic-adds-self-hosted-sandboxes-and-mcp-tunnels-to-claude-managed-agents/), announced at Code with Claude London on May 19 and now in public beta. The pitch is deceptively plumbing-flavored: tool execution can run inside your own perimeter — your VPC, or a managed provider like Cloudflare, Daytona, Modal, or Vercel — while the agent loop itself keeps running on Anthropic's servers. [MCP tunnels](https://www.infoq.com/news/2026/05/claude-mcp-tunnels/) complete the picture: a lightweight gateway inside your network opens a single outbound encrypted connection to Anthropic's router, so internal MCP servers become reachable without inbound firewall rules or public DNS.

Strip the marketing and what you have is a textbook **control-plane / data-plane split**. The control plane — the loop deciding what to do next — lives with the provider. The data plane — where your files, repos, and credentials actually get touched — lives with you. That's not a feature; it's a statement about who owns which failure. When the loop stalls, that's Anthropic's pager. When a tool call leaks a secret, that's yours. Regulated buyers have been holding up agent pilots for exactly this reason — "where does the code execute?" was a political question, not a technical one — and the split is the answer that unblocks them.

## The fork: who do you want holding the loop?

Google answered the same week, and answered differently. [Managed Agents in the Gemini API](https://blog.google/innovation-and-ai/technology/developers-tools/managed-agents-gemini-api/) (May 19) provisions a cloud execution environment with a single API call — but *both* the agent loop and the tool execution run on Google's infrastructure. You define behavior declaratively in versionable [AGENTS.md and SKILL.md](https://agents.md/) files and register the agent; Google runs the whole thing. It's vertically integrated and operationally simple, and it puts your execution inside Google's perimeter, not yours.

Cursor took a third road. [Composer 2.5](https://www.digitalapplied.com/blog/agentic-ai-week-in-review-may-19-23-2026) (May 18) is built on Kimi K2.5 with Cursor's own RL post-training — roughly 85% of its compute went to that — and both the model and the loop are theirs. You're not renting a loop that wraps a frontier model; you're renting a loop fused to a model they trained for it.

So the fork is real and it's three-way:

- **Split (Anthropic):** loop hosted, data plane yours. Best when compliance and data residency dominate.
- **Integrated (Google):** loop and tools both hosted. Best when operational simplicity dominates and your data can live in their cloud.
- **Fused (Cursor):** model and loop co-trained and co-hosted. Best when the loop *is* the product and you want the RL flywheel.

The thing nobody is saying out loud: in all three, **lock-in moved from the model to the loop.** Swapping models is a config change. Swapping the loop means re-implementing orchestration, compaction policy, retry semantics, and the AGENTS.md/SKILL.md surface — which is exactly why providers are racing to host it.

## The loop is now a serving workload

The research side confirms the loop has become infrastructure, because people are now optimizing its *serving* characteristics. ["Parallel Context Compaction for Long-Horizon LLM Agent Serving"](https://arxiv.org/abs/2605.23296) (May 22) treats compaction the way databases treat compaction: a background operation with throughput and tail-latency budgets. The paper's complaint is telling — LLM summarization is "inherently lossy and the blocking call stalls agent inference for tens of seconds," and operators lack fine-grained control over summary volume. Their fix runs compaction in parallel across 8B–120B backbones, trading the synchronous stall for predictable, controllable summary volume.

Read that as a systems paper, not an NLP one. When the loop is hosted, **context management stops being prompt engineering and becomes a serving-layer SLO.** The same shift shows up in memory work like [Memex(RL)](https://arxiv.org/pdf/2603.04257), which scales long-horizon agents via an indexed experience memory so the working context stays small — again, an efficiency-of-serving framing rather than a recall-quality one. Compaction blocking your inference for tens of seconds is a latency bug the provider now owns on your behalf, which is precisely why you'd let them host the loop in the first place.

## What to actually do

Pick the loop deliberately, not by default. If your data can't leave your perimeter, the split model is the only one of the three that lets you adopt a hosted loop without a compliance fight — but verify the loop provider can't see tool *payloads*, only tool *calls*. If you're optimizing for speed of shipping and you already live in one cloud, the integrated model is fine and you should stop hand-rolling orchestration. And whichever you choose, write your behavior down in AGENTS.md/SKILL.md now: it's the one artifact that's portable across all three, and it's the cheapest insurance against the lock-in that just shifted under your feet.

## Worth bookmarking

- [Anthropic self-hosted sandboxes + MCP tunnels](https://the-decoder.com/anthropic-adds-self-hosted-sandboxes-and-mcp-tunnels-to-claude-managed-agents/) — the control-plane/data-plane split, explained
- [MCP tunnels writeup (InfoQ)](https://www.infoq.com/news/2026/05/claude-mcp-tunnels/) — how private MCP access works without inbound rules
- [Managed Agents in the Gemini API](https://blog.google/innovation-and-ai/technology/developers-tools/managed-agents-gemini-api/) — Google's vertically integrated answer
- [Parallel Context Compaction for Long-Horizon LLM Agent Serving](https://arxiv.org/abs/2605.23296) (arXiv 2605.23296) — compaction as a serving SLO
- [Memex(RL): Scaling Long-Horizon LLM Agents via Indexed Experience Memory](https://arxiv.org/pdf/2603.04257) — keeping the working context small
- [AGENTS.md](https://agents.md/) — the portable, provider-agnostic agent definition
