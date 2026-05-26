---
title: "The Agent Trust Stack Just Got Built: Three Weeks in May 2026"
description: "Skill cards, self-hosted sandboxes, MCP tunnels, computer-use verifiers, and a Five Eyes warning all landed in twenty-one days. The boring perimeter around capable agents finally has shape."
pubDatetime: 2026-05-26T11:00:00-07:00
tags:
  - agents
  - security
  - governance
  - mcp
  - skills
featured: false
draft: false
---

Capability stopped being the bottleneck for agents about a year ago. What was missing was the boring scaffolding wrapped around capability: where the agent actually runs, what bundle of instructions it is allowed to load, who signed that bundle, how you reach a private API without poking a hole in the firewall, and how you prove after the fact that a six-hour trajectory actually succeeded. Three weeks in May 2026 filled in most of that layer at once. None of it was a model release. All of it matters more than a model release would have.

Four shipments line up too neatly to be coincidence: the [Five Eyes "Careful Adoption of Agentic AI Services"](https://www.cisa.gov/news-events/news/cisa-us-and-international-partners-release-guide-secure-adoption-agentic-ai) joint guidance (May 1), Microsoft Research and Browserbase's [Universal Verifier paper](https://arxiv.org/abs/2604.06240) (Apr–May), Anthropic's [self-hosted sandboxes and MCP tunnels](https://www.infoq.com/news/2026/05/claude-mcp-tunnels/) at Code with Claude London (May 19), and [NVIDIA-Verified Agent Skills](https://developer.nvidia.com/blog/nvidia-verified-agent-skills-provide-capability-governance-for-ai-agents/) with cryptographically signed skill cards (May 22). Read together, they describe the same architecture from four angles. Worth taking that architecture seriously.

## Provenance moved down to the capability bundle

The interesting move with [NVIDIA Verified Agent Skills](https://github.com/NVIDIA/skills) is not that NVIDIA has a skills repo. It is that every skill ships with a machine-readable skill card — ownership, dependencies, license, technical limits, identified risks, mitigations — and a cryptographic signature, with a "SkillSpector" tool that scans the bundle for vulnerabilities, dangerous code patterns, hidden instructions, and prompt-injection payloads. The format builds on the open [agentskills.io](https://agentskills.io/specification.md) `SKILL.md` standard already supported by Claude Code, Codex, Cursor, and Copilot.

That last detail is the load-bearing one. Skills are how you scale an agent past the ~30-tool ceiling without context exploding — the agent reads the full `SKILL.md` only when the task matches. But skills are also the perfect supply-chain attack surface: a folder of natural-language instructions plus optional code, loaded into the loop on demand, often pulled from a registry. Up to May, the security model was "I trust the GitHub repo." That is not a security model. Signed skill cards with risk metadata are. Expect this to be how enterprise procurement starts gating which capabilities an agent is allowed to discover.

## The runtime moved inside the customer perimeter

Anthropic's announcement at [Code with Claude London](https://thenewstack.io/anthropic-mcp-tunnels-sandboxes/) was framed as two features and is really one architectural shift. Self-hosted sandboxes (public beta) move tool execution out of Anthropic's infrastructure and into the customer's — on Cloudflare, Daytona, Modal, Vercel, or self-managed compute — while Anthropic continues to handle orchestration, context, and recovery. MCP tunnels (research preview) let agents reach private MCP servers via an outbound encrypted gateway: no inbound firewall rule, no public exposure of internal databases or ticketing systems.

The combination is the answer to the six-week security review that has been quietly killing every enterprise agent pilot since late 2025. Once the actual code execution lives inside your VPC and your MCP server is reached over an outbound tunnel, the conversation with the security team shifts from "let us in" to "approve this gateway." That is a tractable conversation. It is also why this is more important than another point on OSWorld — capability without a runtime story is a demo.

The same week, Microsoft Research [open-sourced Fara-7B](https://github.com/microsoft/fara), a small computer-use model designed for on-device execution. Different vendor, same pressure: get the agent closer to where the data lives.

## Trajectories became verifiable

[The Art of Building Verifiers for Computer Use Agents](https://www.microsoft.com/en-us/research/articles/the-art-of-building-verifiers-for-computer-use-agents/) is the paper that should be on every agent team's reading pile. The headline result is that Microsoft Research and Browserbase's Universal Verifier matches human–human agreement on CUAVerifierBench (246 labeled trajectories — 140 internal, 106 from Browserbase) while cutting false positives to near zero, well beyond WebVoyager and WebJudge baselines. The interesting bit is the four design principles: non-overlapping rubric criteria, separate process and outcome rewards, an explicit cascading-error-free strategy for distinguishing controllable from uncontrollable failure, and divide-and-conquer context management so the verifier actually attends to every screenshot in the trajectory.

Without a reliable verifier, you cannot train computer-use models with RL (no usable reward), cannot evaluate them honestly (LLM-as-judge inflates), and cannot ship them into production loops that report success back to a human. The Universal Verifier is open-sourced. Treat it as the missing oracle that turns a brittle screen-clicker into something you can grade. Bonus: DeepMind's [Co-Scientist](https://deepmind.google/blog/co-scientist-a-multi-agent-ai-partner-to-accelerate-research/), published in Nature on May 19, leans on the same idea at a different layer — a Reflection agent plus an Elo-style "idea tournament" Ranking agent that act as verifiers over scientific hypotheses, with one resulting candidate (Vorinostat for liver fibrosis) cutting TGFβ-induced chromatin changes 91% in hepatic organoids. The verifier-in-the-loop pattern is no longer optional.

## Governance became a national-security topic

The 30-page [Five Eyes joint guidance](https://www.theregister.com/security/2026/05/04/five-eyes-warn-agentic-ai-is-too-dangerous-for-rapid-rollout/5229103) is worth reading once. The substance is unglamorous — zero trust, defense in depth, least privilege — but the meta-signal is loud: this is the first time the US, UK, Canada, Australia, and New Zealand cybersecurity agencies have issued coordinated policy on a single AI attack surface. They name five risk categories — over-privileged agents, design and configuration flaws, behavioral risk (agents pursuing goals their designers did not predict), structural risk from interconnected agent networks, and accountability gaps in inspecting decisions and parsing logs.

You do not have to live in a country that signed this guidance for it to matter. Your enterprise customers' procurement teams read these documents and convert them into RFP checkboxes inside of a quarter. That is the timescale the trust stack is now operating on.

## What this means for builders

Stop treating runtime, provenance, verification, and governance as future work. As of three weeks ago, every piece has a vendor-blessed and/or research-blessed reference implementation. The questions to answer for your next agent build:

- Where do tool executions run, and who owns that environment?
- How does the agent reach internal systems, and what is inbound vs. outbound?
- Are the skills the agent can load signed, scanned, and pinned to versions you reviewed?
- Do you have a verifier that scores trajectories independently of the agent that produced them?
- Can you produce a parseable audit log on demand?

If any of those is "we'll figure it out," you have homework. The capability ceiling moved up. The trust floor moved up faster.

## Worth bookmarking

- [NVIDIA-Verified Agent Skills announcement](https://developer.nvidia.com/blog/nvidia-verified-agent-skills-provide-capability-governance-for-ai-agents/) — what signed skill cards and SkillSpector look like in practice.
- [Anthropic self-hosted sandboxes + MCP tunnels](https://www.infoq.com/news/2026/05/claude-mcp-tunnels/) — the runtime-inside-the-perimeter pattern, with the four launch partners listed.
- ["The Art of Building Verifiers for Computer Use Agents"](https://arxiv.org/abs/2604.06240) — Universal Verifier paper and the CUAVerifierBench benchmark, both open-sourced.
- [CISA "Careful Adoption of Agentic AI Services"](https://www.cisa.gov/news-events/news/cisa-us-and-international-partners-release-guide-secure-adoption-agentic-ai) — the Five Eyes 30-page joint guidance.
- [DeepMind Co-Scientist (Nature)](https://deepmind.google/blog/co-scientist-a-multi-agent-ai-partner-to-accelerate-research/) — multi-agent hypothesis generation with explicit Reflection + Ranking verifier roles.
- [agentskills.io specification](https://agentskills.io/specification.md) — the open `SKILL.md` standard that NVIDIA's verified skills build on, supported across Claude Code, Codex, Gemini CLI, and Cursor.
- [microsoft/fara](https://github.com/microsoft/fara) — Fara-7B, the on-device computer-use model published alongside the verifier work.
