---
title: "MCP Just Crossed the Inflection Point"
description: "Fourteen months in, the Model Context Protocol stopped being a curiosity and started being plumbing. Here's what changed over the holidays — registries, governance, and the first scaling pains."
pubDatetime: 2026-01-15T08:00:00-08:00
tags:
  - mcp
  - agents
  - protocols
  - infrastructure
  - anthropic
featured: false
draft: false
---

The first weekend of 2026 I ran `mcp list` against the [official registry](https://registry.modelcontextprotocol.io/) and got back 2,047 servers. A year ago that number was 714. PulseMCP — which indexes the long tail — passed 15,000 a week before Christmas. Smithery is north of 7,000. Composio claims 20,000+ tools across 1,000+ toolkits. The pace isn't slowing down; if anything, the holidays were a step function.

MCP crossed the inflection point sometime in November and we mostly didn't notice because Code with Claude isn't until May. But the shape of the ecosystem in mid-January 2026 is fundamentally different from where it was at the start of 2025, and worth a careful look before the spring conference cycle scrambles everything again.

## The governance change that mattered

The single most consequential MCP event of the last quarter didn't ship a feature. On December 10, 2025, Anthropic [donated the protocol to the Agentic AI Foundation (AAIF)](https://registry.modelcontextprotocol.io/) under the Linux Foundation. Steering committee seats went to Anthropic, OpenAI, Google, Microsoft, Cloudflare, and a rotating set of community maintainers.

This is the same move OpenTelemetry made with tracing, gRPC made with RPC, and Kubernetes made with container orchestration. Single-vendor protocols don't scale into industry standards. Foundation-governed protocols do. The cynical read — "Anthropic gave away a winning bet" — misses the mechanics. The protocol *needed* to be vendor-neutral to be adopted by OpenAI's Responses API, Google's ADK, and the dozen enterprise platforms that wouldn't ship Anthropic-branded plumbing in their stack. The donation was the unlock for everything that's happening now.

What it didn't do: settle the registry question. There is still no single source of truth for "which MCP servers exist." The AAIF runs the official registry as a curation layer (~2,000 servers, all with verified maintainers and security review). The community runs PulseMCP (everything installable, ~15,000 servers, quality varies wildly). Smithery sits in the middle (~7,300, marketplace-style with install-button UX). Composio bundles MCP servers into toolkits aimed at framework users.

Picking the right registry is now a design decision, not just a discovery question.

## What's actually in the registry

If you skim the top 200 servers by install count across registries, three categories dominate:

| Category | Examples | Why it dominates |
|----------|----------|------------------|
| **Code & dev infra** | GitHub, GitLab, Sentry, Datadog, Kubernetes, Cloudflare | First wave — every dev tool shipped one in 2025 |
| **SaaS surface** | Notion, Linear, Jira, Slack, Salesforce, HubSpot | Where work actually happens for most teams |
| **Data & search** | Pinecone, Weaviate, Tavily, Exa, ClickHouse, Snowflake | Powers the "give my agent a memory" workflows |

Then there's a long tail that's harder to categorize: vertical-specific (financial data via FactSet, Moody's, Kensho; biomedical via PubMed, ChEMBL), hardware bridges (browser-use, Playwright, OS automation), and the increasingly weird "anything you can imagine" tail — MCP servers for SQLite databases that don't exist yet, for spreadsheets, for the user's mom's recipe collection.

The interesting category isn't the most populated one. It's the *governed data* category — official MCP servers shipped by the data provider themselves, with auth, billing, and audit baked into the protocol layer. FactSet, Moody's, Kensho (S&P), Daloopa, Morningstar, Bloomberg, LSEG, Egnyte, PitchBook — every one of these went live in Q4 2025. The mechanics aren't accidental. Selling data to humans means a sales team and a PDF; selling data to agents means an MCP server. The category that didn't exist eighteen months ago is now table stakes for any data provider above a certain size.

## The 66% security number nobody is talking about loud enough

[AgentSeal scanned 1,808 MCP servers in November](https://agentseal.org/blog/mcp-server-security-findings) and found that 66% had at least one security finding. The most common: hardcoded credentials in example configs, lax CORS policies on remote MCP endpoints, unvalidated tool input arguments, and prompt-injection-friendly tool descriptions. About 14% had what they classified as critical findings — things like SSRF via unvalidated URLs or path traversal in file-tool servers.

This is the part of the ecosystem that's still operating like 2014 Node.js. Anyone can publish anything, the registry doesn't lint for security, and the default mental model — "an MCP server is just a thin wrapper around an API" — is exactly wrong. The thin wrapper is the attack surface. A tool description is a prompt. An argument schema is a parser. An output is a payload. Every one of those is a place where a malicious or careless server author can break the agent it talks to.

Two practical implications:

1. **Treat MCP servers as untrusted code by default.** The fact that you `npm install`'d it doesn't change anything. Run them in least-privilege sandboxes. Scope their credentials. Pin versions and review changelogs the way you'd review an npm dependency.
2. **Prefer the AAIF official registry for production.** The curation isn't perfect, but it's the only registry that does any kind of security review at admission. The cost (slower listing, fewer servers) is the feature.

The community is starting to converge on signed-server-manifests and reproducible builds — there's an in-flight [proposal](https://github.com/modelcontextprotocol/modelcontextprotocol) for SLSA-style supply chain provenance — but it's not the default yet. Until it is, assume the registry is the dependency vector.

## The shape problem: still one tool per endpoint

The other unresolved issue is the one I [wrote about in February](/blog/mcp-too-many-tools-problem) — the tool-per-endpoint cliff. Most MCP servers in the registry still ship a tool for every operation. Twenty-tool servers are common. Fifty-tool servers exist. The Cloudflare Code Mode pattern (a `search` + `execute` pair backed by an OpenAPI spec) is gaining traction, but it's a minority approach.

This matters because the average production agent now sits at the intersection of 6-12 MCP servers. Pick six 20-tool servers and your context overhead is 120 tool descriptions before the user has said anything. Most teams discover this the hard way — the agent works in isolation, gets connected to the production tool surface, and immediately starts hallucinating tools or getting confused about which one to call. Tool selection at scale is the next unsolved problem, and the registries don't push server authors toward smaller surfaces — they push them toward more.

If you're publishing an MCP server in 2026, the cost-of-context lens is the one to optimize for. Two well-designed tools that compose beat fifteen narrow tools that don't.

## What this means for the next quarter

A few moves worth making while the dust is still settling:

**Audit your MCP dependency graph.** Same way you audit npm dependencies. Which servers are you depending on? Who maintains them? When were they last updated? Are they listed in the AAIF registry? If not, why not. The half-finished version of this work is now production tech debt.

**Stop treating discovery as a manual problem.** With 15,000+ servers across registries, "which MCP server should I use for X" is a search problem. Tools like [MCP.so](https://mcp.so) and the AAIF registry have search APIs that are themselves accessible via MCP. Build a meta-server. Make discovery part of the agent loop rather than a human-in-the-loop ceremony.

**Bet on the open governance future.** If you're building an agent platform, the AAIF protocol path is the one that compounds. Single-vendor extensions and proprietary protocol variants will be tempting in the short run and lonely in the long run.

The protocol is fourteen months old and already has the shape of standard infrastructure. The interesting questions for 2026 aren't whether MCP wins — that's done. They're whether the registry quality, security model, and tool-surface ergonomics can keep up with the adoption curve. The early-2014 Node.js comparison is the right reference point. So is the warning that comes with it.

## Worth bookmarking

- [Official MCP Registry](https://registry.modelcontextprotocol.io/) — AAIF-curated, ~2,000 servers
- [PulseMCP](https://www.pulsemcp.com) — long-tail index, ~15,000 servers
- [Smithery](https://smithery.ai) — marketplace UX, install-button discovery
- [AgentSeal MCP security findings](https://agentseal.org/blog/mcp-server-security-findings) — the 66% number, and what to do about it
- [MCP Specification](https://spec.modelcontextprotocol.io) — the actual protocol, now AAIF-governed
- [Cloudflare Code Mode write-up](https://blog.cloudflare.com/code-mode/) — the search+execute alternative to tool-per-endpoint
