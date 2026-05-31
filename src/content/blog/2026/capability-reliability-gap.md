---
title: "Capability Went Up. Reliability Didn't. That's the Agent Problem Now."
description: "New work argues agents are measured wrong: accuracy keeps climbing while consistency, robustness, and predictability barely move. The fix is architectural."
pubDatetime: 2026-05-31T11:00:00-07:00
tags:
  - agents
  - reliability
  - planning
  - evals
featured: false
draft: false
---

Here is the uncomfortable finding from the last two weeks of agent research: making a model smarter has stopped making your agent more dependable. A single accuracy number on a leaderboard can rise while the thing you actually care about — whether the agent does the same correct thing twice in a row — stays flat. If you run agents in production, you have probably already felt this. The model upgrade landed, the demo got better, and the 3 a.m. pages did not stop.

A growing body of work is now treating reliability as a first-class property to be measured and engineered, separate from raw capability. That reframing, plus a quieter shift in how planning agents are built, is the most useful thing happening in the field right now.

## Reliability is its own axis, and we have been ignoring it

The clearest articulation comes from [Towards a Science of AI Agent Reliability](https://arxiv.org/abs/2602.16666v1) (Rabanser, Kapoor, Narayanan, and colleagues). Their argument is that standard evaluation compresses agent behavior into a single success metric, and that number hides almost everything operationally important. They decompose reliability into four dimensions — consistency, robustness, predictability, and safety — and propose twelve concrete metrics underneath them. Then they evaluate fourteen agentic models on two benchmarks and report the line that should be on every platform team's whiteboard: recent capability gains have only yielded small improvements in reliability.

That gap is not a measurement artifact. It is the lived experience of shipping agents. A pass@1 score tells you nothing about variance across runs, behavior under a slightly perturbed prompt, or whether failures are the predictable kind you can guardrail or the random kind you cannot. The recent [agent benchmark reckoning](/posts/agent-benchmark-reckoning/) exposed how inflated the leaderboards were; this is the next layer down. Even an honest accuracy number is the wrong number if you are trying to operate a system that has to behave the same way on Tuesday as it did on Monday.

The practical takeaway is to stop reporting a single score. Run the same task many times and report the distribution. Track consistency (same input, same output) and robustness (paraphrased input, same output) as separate dashboards. An agent that is 90% accurate but only 60% consistent is a worse production system than one that is 80% accurate and 95% consistent, because you can build around predictable behavior and you cannot build around a coin flip.

## The architectural answer: get the LLM out of the hot path

If reliability is the bottleneck, the structural fix is to use the model less at runtime. [Planning in the LLM Era: Building for Reliability and Efficiency](https://arxiv.org/abs/2605.21902) (Katz, Kokel, Srinivas, and Sohrabi, presented at ICAPS 2026) makes this concrete for planning agents. Direct plan generation — ask the LLM for the steps and execute them — is, in their words, unsound and incomplete by its very nature. It burns tokens and still fails on novel problems.

Their proposed shift is to move the model from inference time to solution-construction time. Instead of generating a plan, the LLM generates a *symbolic solver* for a whole family of problems. That solver can be verified once and then run cheaply and deterministically at inference, with minimal or no LLM calls in the loop. You pay the unreliable, expensive model exactly once, up front, where its output can be checked — and you get a fast, auditable artifact to run forever after.

This is the same instinct as treating [verification as the agent's substrate](/posts/verification-is-the-agent-substrate/), pushed one step further: don't just check the model's output, replace the model's runtime role with a checkable program. It rhymes with the broader [code-mode](/posts/mcp-too-many-tools-problem/) direction the ecosystem has been moving toward — generated, inspectable code is more reliable than an opaque token stream because you can read it, test it, and pin it.

## Reliability is becoming product infrastructure

The vendor releases this month point the same way, even when the marketing leads with capability. Anthropic's Managed Agents now run in sandboxes you control, connect to your private MCP servers, and emit webhooks for multi-agent orchestration — control-plane features, not smarter-model features. OpenAI's enterprise **Frontier** platform is pitched on shared context and governed deployment. Google's [Gemini Spark](https://www.cnbc.com/2026/05/19/google-ai-ultra-gemini-spark-omni.html) agent leans on reasoning across connected apps. The capability race continues, but the money is increasingly spent on making agents observable, sandboxable, and predictable — because that is what blocks deployment.

None of this means capability stopped mattering. It means the binding constraint moved. For the past year the question was "can the agent do the task at all." For the teams shipping now, the question is "will it do the task the same way ten thousand times, and can I prove what it did when it didn't." Measure that axis directly, design to keep the model out of the deterministic parts of your pipeline, and treat every run as a sample from a distribution rather than a verdict. The agents that win the next year will not be the most capable on a single try. They will be the most boring.

## Worth bookmarking

- [Towards a Science of AI Agent Reliability](https://arxiv.org/abs/2602.16666v1) — the four-dimension, twelve-metric reliability framework and the capability/reliability gap finding.
- [Planning in the LLM Era: Building for Reliability and Efficiency](https://arxiv.org/abs/2605.21902) — ICAPS 2026 paper on moving the LLM from inference to solver construction.
- [Survey on Evaluation of LLM-based Agents](https://arxiv.org/abs/2503.16416) — a thorough map of agent eval benchmarks across planning, tool use, memory, and reflection.
- [VIGIL: A Reflective Runtime for Self-Healing Agents](https://arxiv.org/pdf/2512.07094) — a runtime that supervises a sibling agent and performs autonomous maintenance.
- [Google's Gemini Spark and 3.5 Flash launch](https://www.cnbc.com/2026/05/19/google-ai-ultra-gemini-spark-omni.html) — the agent-as-product framing from the May releases.
