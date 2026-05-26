---
title: "Sandbox Execution: Code Interpreters Grew Up"
description: "Firecracker microVMs, gVisor containers, persistent workspaces, and the $24M Series A nobody quite expected. The sandbox layer beneath every serious agent — and how to pick the right one."
pubDatetime: 2026-04-10T08:00:00-07:00
tags:
  - agent-tools
  - agents
  - sandbox
  - infrastructure
  - e2b
  - modal
featured: false
draft: false
---

Daytona raised a $24M Series A in February. E2B has been running production sandboxes for Anthropic and OpenAI under the hood for over a year. Modal added Python sandboxes for agent code execution and the demand has reportedly outstripped their initial capacity planning. There's a quiet infrastructure layer beneath every serious agent right now, and it's getting big enough that the people building it stopped having to explain themselves.

This post is about that layer — what it does, who's building it, and how to pick the right one for what you're doing.

## Why sandboxes are everywhere now

A year ago "sandboxed code execution" was a feature in two places: ChatGPT's Code Interpreter and a handful of agent frameworks that bolted on an `exec()` step. Today it's a category. The reason is mechanical: every serious agent now writes code as part of its work. Some of that code is the task ("write a Python script that processes this CSV"). Some of it is the *mechanism* — the [Code Mode pattern](/blog/mcp-too-many-tools-problem) where the agent's actions are JavaScript snippets that call APIs, the [sandbox-everything pattern](https://www.anthropic.com/engineering/code-execution-with-mcp) where MCP tool results are loaded into a sandbox and the agent queries them with code instead of consuming them as tokens, the long-running [bash-tool-via-sandbox pattern](https://github.com/anthropics/claude-code) Claude Code uses internally for shell operations.

Once code is the substrate, "where does the code run" becomes a serious question. The local-process answer fails at the first prompt injection. The "spin up a fresh container per task" answer fails on cold-start latency. The "shared sandbox" answer fails on state leakage. The right answer requires actual engineering.

## The three architectural choices

The sandbox vendors split along a clean axis: what the isolation primitive is.

**Firecracker microVMs (E2B, Modal in `vm` mode, some Daytona configurations).** Each sandbox gets its own kernel. Hardware-level isolation via KVM. Cold start: 100-300ms typically. Memory floor higher than containers because each VM allocates its own kernel. The best isolation primitive in the field, and the right default for any code that comes from an LLM you don't fully trust.

**gVisor containers (Modal in default mode, some E2B configurations).** Kernel-level isolation via a user-space kernel that intercepts syscalls. Cold start: tens of ms. Better density than microVMs. Slightly weaker isolation guarantees, but well-vetted (gVisor has been Google's container security primitive for the better part of a decade).

**Standard Docker containers (Daytona's primary mode, most homegrown setups).** Process-level isolation, shared host kernel. Cold start: sub-100ms with snapshotting. Best density. Weakest isolation — sufficient for trusted code or for use cases where the threat model doesn't include adversarial agent outputs.

The trade-off is the same one you've seen in cloud infrastructure for fifteen years: stronger isolation costs more in latency and density. The interesting thing about the agent-sandbox category is that the cost difference is small in absolute terms — sub-300ms cold start for microVMs is fine for almost any agent loop — and the consequences of getting isolation wrong are large. The default for LLM-generated code should be microVMs unless you have a specific reason otherwise.

## E2B: the substrate everyone forgets is there

E2B is the closest thing the category has to AWS — the boring infrastructure layer that other products are built on. The architecture: Firecracker microVMs, Python and Node SDKs, ~150ms cold starts, persistent sessions you can hold open for hours.

What makes E2B work in production:

**Session persistence.** A sandbox that lives across multiple agent steps without paying cold-start cost on each call. The agent writes a file in step 1, runs a script in step 3, queries the result in step 5 — same sandbox, accumulated state. This is what made E2B win at "agent that uses a sandbox" vs. "agent that calls exec() repeatedly."

**Native bindings to the dominant agent frameworks.** OpenAI Agents SDK, LangGraph, the Claude Agent SDK — all have first-class E2B integrations. The sandbox is one line of agent code, not a custom MCP server.

**Predictable resource model.** You pay for sandbox runtime, not per-call. A long-running task that holds a sandbox for ten minutes is cheaper than 30 short cold starts.

The thing E2B is *not* great at: GPU workloads, persistent state across days, or sandboxes that survive their parent process. For those, look elsewhere.

## Modal: when you need GPUs

Modal entered the sandbox category through a side door. They were a serverless ML platform with great GPU support, added Python sandboxes for agent use, and the existing GPU plumbing meant their sandboxes could come with H100s attached — no other vendor in this space ships GPU access as a first-class feature.

That matters more than it sounds. A growing share of agent code is "run a small model locally inside the sandbox" — for embedding, for classification, for image processing — and CPU-only sandboxes turn that work into a "call an external API" task that's slower and leakier than just running the model where the agent's working.

Modal's isolation primitive is gVisor by default, with optional microVM mode. The cold-start story is good (sub-second consistently). The cost story is better for sustained workloads than for spikey ones — Modal's pricing model rewards long-running sandboxes more than rapid-fire short ones.

If your agent's work involves any local model inference, GPU rendering, or compute-heavy data processing, Modal is the path of least resistance. For pure "run this Python script and read the output," E2B is leaner.

## Daytona: the dev-environment pivot

Daytona is the interesting story in this category because of the pivot. They started 2025 as a dev-environment platform — Codespaces / Gitpod competitor — and through Q3-Q4 reoriented around AI agent sandboxes. The Series A in February was the validation.

The architecture is different in a load-bearing way: Daytona's sandboxes are *persistent workspaces*, not ephemeral execution environments. The agent's sandbox can live for days or weeks. It accumulates files, installed packages, configured services. The mental model is "the agent has a desktop computer" rather than "the agent has a fresh VM per task."

This matters for a specific class of agent: long-horizon coding agents, agents that work on a codebase over time, agents that need to install and configure tools as part of their work. For these, the dev-environment heritage pays off — Daytona was already good at "give a process a stable workspace" before it pivoted.

The cost: weaker isolation by default (Docker containers, shared kernel), longer cold starts for fresh workspaces, and a model that's optimized for sessions in the minutes-to-days range rather than the milliseconds-to-minutes range.

## The matrix

Picking a sandbox is mostly about three questions: how long does the sandbox need to live, how strong does isolation need to be, and do you need GPU.

| Use case | Primary choice | Why |
|----------|---------------|-----|
| Short-lived per-task execution, untrusted code | E2B | Firecracker isolation, fast cold start, mature SDK |
| Long-lived coding agent workspaces | Daytona | Persistent workspace model, dev-tool heritage |
| GPU-bound model inference inside sandbox | Modal | First-class GPU access, gVisor or microVM choice |
| Trusted code, max density, internal tools | Docker on your own infra | No vendor cost, weakest isolation acceptable for trusted code |
| Anthropic-native agent | [Anthropic Sandbox](https://www.anthropic.com/news/secure-sandboxes-private-mcps) | First-party integration, May 6 announcement |

The Anthropic sandbox primitive — [announced at Code with Claude on May 6](https://www.anthropic.com/news/secure-sandboxes-private-mcps) — is worth a note even though it's at the edge of this post's timeframe. It bakes sandbox execution into Claude Managed Agents with first-party billing and a private MCP integration. If you're already deep in the Anthropic stack, it's the path of least integration friction.

## What the sandboxes actually run

A composite of the workloads I've seen running in production sandboxes:

**Tool-result analysis.** The agent calls an MCP tool that returns a 50K-line CSV. Instead of sending the CSV to the LLM, the runtime drops it in the sandbox and the agent writes Python to query it. Saves enormous token cost. This is the use case that's growing fastest.

**Code Mode execution.** The agent's "action" is a JavaScript snippet that calls an API. The sandbox runs the snippet, returns the result. The agent doesn't see the raw HTTP responses.

**Iterative code authoring.** The agent writes a script, runs it, sees the error, edits the script, runs it again. Five-step debugging loops are normal. The sandbox is the workspace; persistence across the loop matters.

**Local model inference.** Small classifier or embedding model runs inside the sandbox. The agent uses it like any other tool. Modal is where this happens; E2B has it via custom images.

**Browser automation.** Headless Chrome inside the sandbox, controlled by Browser Use. The browser session has its own state, accessible to the agent through Browser Use's API.

**Long-running research.** A multi-hour workflow that downloads data, processes it, writes intermediate files, writes a report. Daytona's bread and butter. The workspace persists; the agent can pick up across sessions.

## The security model

This is the section where most teams have gaps and most posts hand-wave.

**Outbound network from sandboxes.** A sandbox that can talk to the open internet is a sandbox that can exfiltrate. The default should be a deny-list-then-allow-list model: deny outbound, then allow specific endpoints. E2B, Modal, and Daytona all support this; not all teams turn it on.

**Filesystem reach.** A sandbox should not have access to the host filesystem. Should sound obvious. It often isn't, because debugging is easier when you can mount things. The discipline: mounts are for human-debug mode only, not for production runs.

**Credential handling.** The agent might need a credential to call an API from inside the sandbox. Don't put the credential in the sandbox env vars — that means any code the agent runs can read it. Use a proxy pattern: the credential lives outside the sandbox, the agent makes a request through a proxy that adds the credential.

**Egress logging.** Every outbound call from the sandbox should be logged. This is your audit trail when something goes wrong. E2B and Modal expose this; building it on Docker takes work.

**Time limits.** Sandboxes should have hard wall-clock limits. An agent that gets stuck in a loop and runs for six hours in your sandbox is one that's costing you money and possibly causing other problems. Cap it; let the agent restart with backoff.

The threat model: the code running in the sandbox is the agent's output, which is influenced by the user's prompt, which can come from anywhere. Treat it as adversarial. Most of the time it isn't. The cost of being wrong when it is is very high.

## What's coming

A few near-horizon developments worth watching:

**Cross-sandbox state protocols.** There's an [in-flight standard](https://github.com/agentic-ai-foundation/sandbox-state) for sandboxes to expose their workspace state to other agents — a way for an agent that finished its work to hand off the sandbox to a different agent, or for a checkpoint/replay system to capture sandbox state. Not stable yet; would be huge if it lands.

**Sandbox-as-MCP-server.** Several teams (E2B included) are exposing the sandbox itself as an MCP server. The agent talks to the sandbox via standard MCP calls. Lowers the integration cost; lets non-framework agents use sandboxes the same way framework-bound ones do.

**Per-tenant resource isolation.** As sandbox volumes grow, multi-tenant isolation matters. The microVM vendors handle this at the kernel boundary. The container vendors are catching up via cgroup v2 quotas and stronger seccomp profiles.

**The model-inside-sandbox pattern.** Small specialized models run inside the sandbox as part of the agent loop. This is the "agent has access to local models" story, and it's where Modal's GPU access compounds.

## What to do this quarter

If you're shipping agents that execute code:

1. **Default to microVM isolation for LLM-generated code.** The latency cost is small. The security cost of getting it wrong is large.
2. **Treat sandbox persistence as an architectural choice.** Short-lived per-task is one shape. Long-lived workspace is another. Pick on purpose.
3. **Lock down egress before you launch.** Deny-list-first. Allow-list the endpoints your agent actually needs.
4. **Pick a vendor; don't roll your own.** The substrate work in this category is real. The Daytona pivot, the E2B production volume, the Modal GPU integration — these are not weekend projects. Use them.

The sandbox layer is the part of the agent stack that nobody talks about because it's working. That's the highest praise infrastructure can get. The category is mature enough that picking the wrong vendor will hurt you; the right vendor for your workload will mostly stay out of your way and let you build the agent.
