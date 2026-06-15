---
title: "Code Is the Action Space Now"
description: "Frameworks are quietly replacing JSON tool calls with generated code. That collapses turns and tokens — and pushes isolation down to the single call."
pubDatetime: 2026-06-15T11:00:00-07:00
tags:
  - agents
  - tool-use
  - sandbox
  - security
  - infrastructure
featured: false
draft: false
---

For two years the agent's action was a JSON blob: the model emitted `{"tool": "search", "args": {...}}`, the runtime ran it, and the result came back as another message. Every tool call was a round trip through the model. The last few weeks made it clear that pattern is being retired in the places that ship. At [BUILD 2026 on June 3](https://devblogs.microsoft.com/agent-framework/microsoft-agent-framework-at-build-2026-announce/), Microsoft's Agent Framework graduated CodeAct — the model writes a short Python program that calls your tools via `call_tool(...)`, runs it once in a sandbox, and returns a consolidated result. The action stopped being a structured call and became a piece of code. That sounds like a syntax change. It is actually a change in where the cost, the isolation, and the attack surface all live.

## The inversion: from a call per turn to a program per turn

The motivation is mechanical, not aesthetic. When tools are JSON calls, a five-step task is five inference passes, and every intermediate result — the full 40-row query, the entire file — flows back through the context window. That is the bloat Anthropic measured last fall in [code execution with MCP](https://www.anthropic.com/engineering/code-execution-with-mcp): a workflow that pushed tool definitions and intermediate data through the model burned ~150K tokens; rewritten so the model writes code against filesystem-style MCP APIs, it used ~2K. The large transcript never touches the model — only the final status and a small sample do. Microsoft's CodeAct benchmark reports the same shape on a representative workload: [latency down 52% and tokens down 64%](https://devblogs.microsoft.com/agent-framework/codeact-with-hyperlight/) versus sequential tool calling. When Claude orchestrates 20-plus tool calls inside one code block via [programmatic tool calling](https://www.anthropic.com/engineering/advanced-tool-use), it eliminates 19-plus inference passes.

This is not a niche optimization; it is the direction the literature has been pointing. A March survey, [The Evolution of Tool Use in LLM Agents](https://arxiv.org/abs/2603.22862), frames the whole field's shift as moving from "could the model pick one correct tool" to multi-tool orchestration "over long trajectories with intermediate state, execution feedback, changing environments." Code is the natural substrate for that: loops, conditionals, and data flow between tools are first-class, not something you simulate by feeding results back as text. Once you accept that the agent's job is orchestration, expressing the orchestration as code instead of as a chain of model turns is the obvious move.

## The consequence nobody planned for: isolation collapses to the call

When the action was JSON, the runtime knew exactly what would happen — it dispatched a named function with typed args. When the action is arbitrary generated code, the runtime knows nothing until it runs. That breaks the isolation model. The old [sandbox debate](/blog/sandbox-execution-grew-up) was framed at the task level: a fresh container per task fails on cold-start latency, a shared sandbox fails on state leakage. CodeAct forces a finer granularity, because now *every action* is untrusted code, not just the occasional "run this script" task.

The answer that arrived with it is per-call isolation. Microsoft's CodeAct runs each `execute_code` block in a fresh [Hyperlight](https://devblogs.microsoft.com/agent-framework/codeact-with-hyperlight/) micro-VM — its own memory, no host filesystem beyond explicit mounts, no network beyond an allowlist — and the framing is the part worth internalizing: the sandbox is "cheap enough to be disposable and strict enough to be the default." The key architectural trick is that the *model-generated code* runs sandboxed while the *actual tools* execute on the host with full privileges; `call_tool` is the bridge across the boundary. The unit of isolation has dropped from the task to the single tool-orchestration step. That is the real news under the latency numbers.

## And the security model inverts with it

Here is the uncomfortable corollary. When the action is code, a prompt injection is no longer "the agent called the wrong tool" — it is arbitrary code execution. The sandbox boundary is now the security boundary, and 2026's vulnerability disclosures are a steady drumbeat of what happens when that boundary is thin. The [vm2 CVEs](https://thehackernews.com/2026/05/vm2-nodejs-library-vulnerabilities.html) (CVE-2026-43997 at CVSS 10.0) turn a sandbox escape into host RCE; in agent frameworks where prompts influence executable logic, that converts a prompt injection directly into machine takeover. [CrewAI's SandboxPython fallback](https://www.thaicert.or.th/en/2026/04/02/multiple-vulnerabilities-in-crewai-allow-sandbox-escape-and-remote-code-execution-via-prompt-injection/) let attackers execute arbitrary code via C function calls under indirect injection. Google's Antigravity was shown to be [injectable even in its highest security mode](https://www.pillar.security/blog/prompt-injection-leads-to-rce-and-sandbox-escape-in-antigravity), because guarding shell commands does nothing when native tool invocations reach the same effect outside the control boundary.

This is no longer theoretical. On May 10, Sysdig documented the [first live LLM-agent intrusion in the wild](https://www.sysdig.com/blog/ai-agent-at-the-wheel-how-an-attacker-used-llms-to-move-from-a-cve-to-an-internal-database-in-4-pivots): an agent went from a CVE on an exposed notebook to exfiltrating an internal PostgreSQL database in under an hour, running four pivots — credential theft, SSH key retrieval from Secrets Manager, lateral movement, exfiltration — with no human directing the steps. The attacker did not replace their team with AI; they replaced their *scripts* with it. That is exactly the capability CodeAct gives a legitimate agent, pointed the other way.

So the two stories are one story. The same property that makes code-as-action efficient — the model can express arbitrary orchestration — is the property that makes it dangerous when the inputs are adversarial. Per-call micro-VM isolation is not a performance footnote; it is the thing standing between "my agent ran a Python loop" and "my prompt injection ran a Python loop on your host." If you are adopting CodeAct or programmatic tool calling, the question to interrogate is not the token savings. It is: what does the generated code get to touch, and is that boundary re-created fresh on every call or shared across them? The frameworks that get this right make the disposable, deny-by-default sandbox the default. The ones that bolt code execution onto a long-lived process are shipping the next CVE.

## Worth bookmarking

- [CodeAct with Hyperlight](https://devblogs.microsoft.com/agent-framework/codeact-with-hyperlight/) — Microsoft's per-call micro-VM isolation for generated code; read it for the boundary design, not the benchmark.
- [Code execution with MCP](https://www.anthropic.com/engineering/code-execution-with-mcp) and [advanced tool use](https://www.anthropic.com/engineering/advanced-tool-use) — Anthropic's case for code-first agents and programmatic tool calling.
- [The Evolution of Tool Use in LLM Agents](https://arxiv.org/abs/2603.22862) — March survey reframing the field around multi-tool orchestration.
- [Sysdig: AI agent at the wheel](https://www.sysdig.com/blog/ai-agent-at-the-wheel-how-an-attacker-used-llms-to-move-from-a-cve-to-an-internal-database-in-4-pivots) — the first documented autonomous LLM intrusion; the offensive mirror of code-as-action.
- [vm2 sandbox escape CVE wave](https://thehackernews.com/2026/05/vm2-nodejs-library-vulnerabilities.html) and [Antigravity prompt-injection RCE](https://www.pillar.security/blog/prompt-injection-leads-to-rce-and-sandbox-escape-in-antigravity) — why the sandbox boundary is now the security boundary.
