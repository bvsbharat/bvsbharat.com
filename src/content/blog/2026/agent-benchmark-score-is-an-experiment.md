---
title: "Your Agent's Benchmark Score Is an Experiment, Not a Fact"
description: "Recent work shows a single agent leaderboard number is wrong three independent ways: it's noisy, it's overfit, and the judge measuring it is unreliable."
pubDatetime: 2026-06-25T11:00:00-07:00
tags:
  - agents
  - evals
  - benchmarks
  - reliability
  - methodology
featured: false
draft: false
---

Here is the most useful thing the last two weeks of agent research will do for you: it will make you distrust a single benchmark number. Not because the benchmarks are bad, but because the way we read them — one mean score, one run, one leaderboard row — throws away exactly the information you need to make a deployment decision. A pile of recent papers converges on the same uncomfortable conclusion from three different directions. An agent's score is a noisy estimate of an overfit quantity measured by an unreliable instrument. Treat it as a point estimate and you will ship the wrong model.

This is a different claim from the [capability-reliability gap](https://www.bvsbharat.com/posts/2026/capability-reliability-gap/) I wrote about last month. That was about the agent being inconsistent. This is about the *measurement* being broken — you often can't even tell whether you improved.

## The number is noisy, and "temperature zero" doesn't save you

Start with variance, because it's the most concrete. [On Randomness in Agentic Evals](https://arxiv.org/html/2602.07150) (Bjarnason, Silva, and Monperrus at KTH) ran 60,000 trajectories across six agent configurations and measured how much a pass@1 score moves just from rerunning it. The answer: single-run estimates swing 2.2 to 6.0 percentage points depending on which run you happened to grab. The gap between the optimistic bound (pass@k) and the pessimistic one (pass^k) reaches 24.9 points. And the detail that should end the "we run at temperature 0 so it's deterministic" excuse: standard deviation still exceeds 1.5 points at temperature 0, because inference-engine nondeterminism — floating point, batching, parallelism — diverges runs inside the first 1% of tokens, and autoregressive conditioning amplifies it from there.

Their power-analysis table is the part to tape to your wall. To detect a 1% improvement at p < 0.05, you need roughly 36 runs per task. For 2%, nine. For 5%, two or three. Most leaderboards and most internal evals report one. So when you "see" a one-point gain from a prompt change, you are almost certainly looking at noise.

The companion finding comes from [Stochasticity in Agentic Evaluations](https://arxiv.org/html/2512.06710v1), which borrows intraclass correlation (ICC) from the measurement-reliability literature to quantify how much of your observed spread is signal versus jitter. Below 0.50 is poor; you want above 0.75. The kicker is that larger models sometimes show *more* inconsistency, not less — capability and stability are separate axes, and scaling one does not buy you the other.

## The number is overfit to the test you happened to run

Variance is the friendly problem. The deeper one is that even a well-averaged in-sample score does not predict out-of-sample behavior — which is the only thing you actually care about. [Beyond Static Leaderboards](https://arxiv.org/html/2606.19704v1) (Patel et al., June 18) makes this its whole thesis and proposes ranking by *predictive validity*: the correlation between where a configuration lands in-sample and where it lands under distribution shift. Their evidence is brutal. On one competition's execution track, the correlation between public and hidden splits was ρ = −0.13 — statistically indistinguishable from zero, and if anything pointing the wrong way. A top-of-leaderboard configuration carries almost no information about deployment rank.

You can see the same rot in the flagship benchmarks. By mid-2026, contamination had degraded SWE-bench Verified enough that vendors began quietly retiring it, with independent analysis estimating 5–15 points of inflation on post-2023 models, which is why the conversation moved to contamination-resistant sets like [SWE-bench Pro](https://www.morphllm.com/swe-bench-pro) built on private commercial codebases. A score that leaked into training is not a measurement; it's a memory test. The [methodology guides tracking this](https://www.digitalapplied.com/blog/llm-benchmark-methodology-2026-contamination-leaderboard-guide) now treat "is this set contamination-controlled" as the first question, not a footnote.

## The instrument itself is biased

The third failure is the one teams skip because it's recursive: most agent evals at scale use an LLM as the judge, and the judge is a measuring instrument with its own reliability problem. The predictive-validity paper puts a number on it — LLM-as-judge inter-rater agreement sits around 0.61, against 0.74–0.82 for human-human agreement on the same material. You are calibrating a model against a ruler that flexes, and worse, the ruler drifts when you swap judge versions, so a "score improvement" can be the judge changing its mind rather than the agent getting better.

This is why the better evaluation harnesses — [agentevals](https://github.com/langchain-ai/agentevals) for trajectory matching, [promptfoo](https://github.com/promptfoo/promptfoo) and [MLflow's eval](https://mlflow.org/) for CI gating — increasingly support deterministic, programmatic checks alongside the LLM judge. The trajectory-level evaluators matter here: checking *which tools the agent called in what order* is a measurement you can reproduce exactly, unlike asking a model "was this good."

## What to actually do

Stop reporting point estimates. Report a distribution: run each task enough times to make the confidence interval smaller than the effect you're claiming, and use a power analysis to decide how many that is rather than defaulting to one. Gate ship decisions on statistical significance above noise — if the new version's delta isn't separable from variance, you have not measured an improvement, you've measured the dice. Add an out-of-distribution slice — paraphrased prompts, renamed identifiers, a held-out domain — and rank on how stable a configuration is across it, not on its in-sample peak. Pin and version your LLM judge, periodically audit it against human labels, and move whatever you can to deterministic trajectory checks so the instrument stops moving under you. And assume your favorite public benchmark is contaminated until proven otherwise; weight contamination-resistant sets accordingly.

None of this is exotic statistics. It's the experimental hygiene every other empirical field adopted decades ago. Agent evaluation is finally being forced to catch up, because the alternative is shipping on noise and finding out in production.

## Worth bookmarking

- [On Randomness in Agentic Evals](https://arxiv.org/html/2602.07150) — 60k trajectories, the variance numbers, and the runs-per-improvement table.
- [Beyond Static Leaderboards: Predictive Validity](https://arxiv.org/html/2606.19704v1) — why in-sample rank doesn't transfer, and a ranking that accounts for it.
- [Stochasticity in Agentic Evaluations](https://arxiv.org/html/2512.06710v1) — ICC for agent evals, with usable thresholds.
- [SWE-bench Pro](https://www.morphllm.com/swe-bench-pro) — a contamination-resistant coding benchmark on private codebases.
- [agentevals](https://github.com/langchain-ai/agentevals) — trajectory-level evaluators you can run deterministically in CI.
- [Evaluation and Benchmarking of LLM Agents: A Survey](https://arxiv.org/html/2507.21504v1) — the broader map of where agent evaluation is and isn't working.
