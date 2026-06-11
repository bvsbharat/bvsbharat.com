---
title: "The Agent Doesn't Know When It's Failing"
description: "New benchmarks measure calibrated refusal and premature self-stops, and the data says agent confidence signals are broken. Here's how to engineer around it."
pubDatetime: 2026-06-11T11:00:00-07:00
tags:
  - agents
  - calibration
  - reliability
  - evals
  - planning
featured: false
draft: false
---

An agent that succeeds 22% of the time and reports 77% confidence is not just unreliable — it is unreliable in a way that poisons everything built on top of it. Retry loops, escalation gates, human-review queues, model cascades: every one of those mechanisms assumes the confidence signal means something. The research that landed in the first week of June says it mostly doesn't, and — more usefully — the benchmarks have finally started measuring the gap directly. Calibration is becoming a tested capability, not a footnote, and the early numbers are bad enough that you should change how your agent decides to stop, ask, or escalate.

## "Knowing when to stop" just became a measured axis

Two benchmarks from the same week made agent self-judgment an explicit test condition, and they caught the failure from both directions.

The [Agent Planning Benchmark](https://arxiv.org/abs/2606.04874) (June 3) runs 4,209 multimodal cases across 22 domains, and alongside the usual planning settings it deliberately injects broken tools, extraneous tools, and — the interesting part — *unsolvable tasks*. Across twelve models, the systematic weaknesses include long-horizon planning and tool-noise robustness, but the one that should worry production teams is **calibrated refusal**: models keep attempting tasks that cannot be completed instead of recognizing the dead end and saying so. The agent that grinds through forty tool calls on an impossible task isn't being persistent. It's burning your budget because it has no internal signal that says "this isn't working."

[DeployBench](https://arxiv.org/abs/2606.05238) (also June 3) catches the inverse failure. It asks agents to deploy 51 real research artifacts — multi-language toolchains, CUDA dependencies, legacy builds — and state-of-the-art models pass between 7.8% and 51% of tasks. The authors name the dominant failure mode the *completion-judgment problem*: of 154 failures, 97 were the agent stopping itself early, satisfied, because its pre-finish checks validated a weaker target than the task actually required. The agent ran *a* verification. It just verified the wrong claim, and believed the result.

Put the two together and the picture is coherent: agents that won't stop when they should, and stop when they shouldn't. Those are not two bugs. They are one broken faculty — the ability to judge your own state against the actual goal — observed from opposite sides.

## The confidence number is broken in a specific, exploitable way

The cleanest measurement of that faculty comes from [Agentic Uncertainty Reveals Agentic Overconfidence](https://arxiv.org/abs/2602.06948), which extends the old P(IK) — "probability that I know" — idea from single answers to multi-step agentic tasks. The headline numbers are stark: agents that succeed 22% of the time predicting 77% success, and a GPT-5.2-Codex agent predicting 73% success against a true rate of 35% on SWE-Bench-Pro. Overconfidence isn't an occasional miss; it's systematic, and it's roughly the same magnitude as the [capability-reliability gap](/posts/capability-reliability-gap/) the field spent late May worrying about.

Two findings in that paper should directly change how you build. First, *post-execution* self-assessment — the agent reviewing its own completed trajectory — discriminated success from failure no better than *pre-execution* estimates made before any work happened. Staring at your own transcript doesn't help, because the transcript is persuasive: it's full of confident actions and plausible reasoning, which is exactly what a miscalibrated judge wants to see. The model that did the work is the worst-positioned judge of the work. Second, the intervention that calibrated best was adversarial framing — asking the model to *find bugs* in the trajectory rather than rate its confidence. "How confident are you?" produces a politeness ritual. "What's wrong with this?" produces signal. The deeper cause is well documented in the [uncertainty-quantification survey literature](https://arxiv.org/abs/2602.05073): preference training rewards confident-sounding outputs regardless of underlying knowledge, so verbalized confidence is a style, not a probability.

## Stop asking for confidence. Engineer it.

The encouraging part of this research wave is that calibration responds to architecture, not just bigger models.

[Ask or Assume?](https://arxiv.org/abs/2603.26233) (revised June 3) is the pattern done right for coding agents. On an underspecified variant of SWE-bench Verified, a scaffold that *decouples underspecification detection from code execution* — a separate component decides whether to ask a clarifying question, gated on uncertainty — hit a 69.4% resolve rate and nearly closed the gap to fully-specified tasks. Crucially, it conserves questions on easy tasks and spends them on hard ones. The decision to ask is routed through a dedicated, calibrated signal instead of hoping the executor volunteers its doubt mid-task. [Holistic Trajectory Calibration](https://arxiv.org/abs/2601.15778) takes a complementary approach: score process-level features across the whole trajectory — tool errors, backtracking, plan churn — rather than asking for a number at the end.

A practical playbook falls out of all this:

- **Never route on raw verbalized confidence.** It is the least informative signal you can extract from a model, and it's the one most teams use.
- **Separate the judge from the doer.** A fresh-context critic prompted adversarially ("find what's wrong") beats the executor's self-report — same lesson as [verification-as-substrate](/posts/verification-is-the-agent-substrate/), applied to the stopping decision instead of the output.
- **Make "this task may be impossible" a first-class outcome.** APB's calibrated-refusal results say models won't volunteer it; your harness needs an explicit path for it, with budget triggers that force the question.
- **Log predicted-versus-actual success.** A calibration curve per task type is cheap to accumulate and tells you exactly where your agent's self-model diverges from reality — which is where your escalation thresholds should live.

External verification told us to check the agent's work. This research wave is about the cheaper question that comes first: does the agent know when checking is needed? Right now the honest answer is no — but for the first time, that's a number on a benchmark instead of a vibe, and numbers on benchmarks are the things this field actually fixes.

## Worth bookmarking

- [Agent Planning Benchmark](https://arxiv.org/abs/2606.04874) — 4,209-case diagnostic with unsolvable-task and broken-tool settings; calibrated refusal as a tested capability.
- [DeployBench](https://arxiv.org/abs/2606.05238) — research-artifact deployment tasks and the completion-judgment problem behind premature self-stops.
- [Agentic Uncertainty Reveals Agentic Overconfidence](https://arxiv.org/abs/2602.06948) — P(IK) for agents, the 77%-predicted/22%-actual gap, and why adversarial self-review calibrates best.
- [Ask or Assume?](https://arxiv.org/abs/2603.26233) — uncertainty-gated clarification-seeking for coding agents, 69.4% on underspecified SWE-bench Verified.
- [Agentic Confidence Calibration](https://arxiv.org/abs/2601.15778) — trajectory-level calibration features instead of final-answer confidence.
- [Uncertainty Quantification in LLM Agents](https://arxiv.org/abs/2602.05073) — the survey covering foundations and why preference training degrades calibration.
