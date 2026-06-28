---
title: "Agent Security Moved to the Action Layer"
description: "Runtime authorization — intercepting tool calls before they execute — is becoming the real security boundary for agents, and a standard is forming fast."
pubDatetime: 2026-06-28T11:00:00-07:00
tags:
  - agents
  - security
  - runtime
  - authorization
  - governance
featured: false
draft: false
---

The most important shift in agent security this year is not a new model or a smarter prompt. It is a relocation. The boundary that decides whether an agent is allowed to do something has moved out of the prompt and into the action layer — the moment just before a tool call executes. Two things happened in the last few weeks that make this concrete: a research line crystallized around deterministic pre-action authorization, and the Cloud Security Alliance turned one of those specs into a category it intends to certify against. If you build agents, the question is no longer "how do I write a safer system prompt." It is "where does my reference monitor live."

## The prompt was never the boundary

The uncomfortable finding driving all of this is simple. Safety instructions in a system prompt sit *inside* the agent's reasoning loop — the exact place an attacker, or just a confused model, has influence over. They are probabilistic controls, and probabilistic controls leak. The numbers being cited are stark: uninstrumented agents follow their stated policy roughly 48% of the time, while agents fronted by a deterministic reference monitor hit around 93%, with zero violations reported in the instrumented runs. That gap is the whole argument. You cannot ask the thing you are trying to constrain to constrain itself.

The fix is an old idea wearing new clothes. The [reference monitor](https://arxiv.org/pdf/2603.20953) — intercept every privileged request, check it against policy, allow or deny, and make the check impossible to bypass — predates LLMs by half a century. The "Before the Tool Call" work (PCAS, *Policy Compiler for Secure Agentic Systems*) revives it for agents with a declarative policy language and a monitor that evaluates each tool invocation deterministically before execution. The threat classes it targets are the ones that don't show up in single-call testing: privilege escalation through chained tool composition, data exfiltration assembled across steps, and indirect attacks that ride in through one tool and pay off in another. None of those are catchable by inspecting a single prompt. All of them are catchable at the point of action, because that is where intent becomes an irreversible side effect.

## Allow/deny is not enough

What the new specs add on top of the classic reference monitor is a richer decision space and stateful context. The [AARM specification](https://arxiv.org/abs/2602.09433) (Autonomous Action Runtime Management) defines a four-stage loop: intercept the action, accumulate session context, evaluate it against both policy *and* intent alignment, then decide — and crucially, record a tamper-evident receipt of what was decided and why. The decision is not binary. Beyond ALLOW and DENY, you get MODIFY (let it through but rewrite the arguments), DEFER, and STEP_UP (escalate to a human for approval). That vocabulary matters because the interesting agent failures are rarely "do this forbidden thing." They are "do this reasonable thing in a context that has quietly drifted," which is why the threat model explicitly names *intent drift* and the *confused deputy* alongside prompt injection.

This is the part builders should internalize: the dangerous unit is no longer the turn, it's the trajectory. An action that is fine in isolation can be the third move in an exfiltration sequence. A monitor that only sees one call at a time can't tell the difference, so the specs insist on accumulated session context and tamper-evident logging — the audit trail isn't a compliance afterthought, it's the substrate that lets you reconstruct *why* an action was permitted. The same shift toward telemetry-as-enforcement shows up in the [governance-aware agent telemetry](https://arxiv.org/pdf/2604.05119) work, which closes the loop by feeding runtime traces back into the policy that gates the next action.

## A category is forming — maybe too fast

The standardization move is the genuinely new part. On April 29, the [Cloud Security Alliance adopted AARM](https://www.resilientcyber.io/p/aarm-and-the-case-for-standardizing) as a flagship specification, paired it with an Agentic Trust Framework, and became a CVE Numbering Authority for agentic vulnerabilities. The [AARM project](https://aarm.dev/) now reports 75 companies adopting the spec and seven through formal conformance review, with two tiers: a mandatory Core (pre-execution interception, identity binding, tamper-evident records) and an Extended profile adding semantic drift tracking, telemetry export, and least-privilege enforcement. The argument for doing this now is preemptive — lock in a vendor-neutral, model-agnostic interface before the market fragments into a dozen incompatible proprietary "guardrail" products.

Healthy skepticism is warranted. A specification with conformance levels is exactly the kind of thing that attracts checkbox compliance, and the same surveys pushing these standards also note that many shipping "agent guardrail platforms" are prompt-level wrappers or rebranded content filters — runtime enforcement in the marketing copy, system-prompt nagging in the code. The honest engineering question is *where you put the monitor*, because that determines whether it can actually be bypassed. AARM sketches four placements — protocol gateway, SDK instrumentation, kernel eBPF, and vendor integration — each with different trust properties. An SDK hook the agent's own code can route around is not a reference monitor; an eBPF or gateway interceptor outside the agent's process is. If your "authorization layer" lives inside the same loop as the thing it's authorizing, you've reinvented the system prompt with more steps.

Gartner's much-quoted line — that by 2030 half of agent deployment failures will trace to insufficient runtime enforcement — is the kind of prediction that ages either prophetic or embarrassing. But the direction is right. The agents worth deploying are the ones that plan, act, and persist state across systems, and those are precisely the ones a prompt cannot govern. Put the boundary outside the loop, make every consequential action pass through it, and keep the receipt.

## Worth bookmarking

- [Before the Tool Call: Deterministic Pre-Action Authorization (PCAS)](https://arxiv.org/pdf/2603.20953) — the reference-monitor revival and the 48%→93% compliance result.
- [AARM specification (arXiv)](https://arxiv.org/abs/2602.09433) — the four-stage intercept/evaluate/decide/record loop and the ALLOW/DENY/MODIFY/DEFER/STEP_UP decision space.
- [Standardizing Agent Runtime Security (Resilient Cyber)](https://www.resilientcyber.io/p/aarm-and-the-case-for-standardizing) — why CSA adopted AARM and what's still missing.
- [aarm.dev](https://aarm.dev/) — conformance tiers, adoption status, and the threat-class taxonomy.
- [Governance-Aware Agent Telemetry for Closed-Loop Enforcement](https://arxiv.org/pdf/2604.05119) — feeding runtime traces back into policy.
