---
title: "Computer-Use Agents Crossed Human Parity. They Still Click Too Much."
description: "Frontier models now beat the human baseline on OSWorld-Verified — but the benchmark just got rebuilt, and the architecture quietly shifted off pixels."
pubDatetime: 2026-06-27T11:00:00-07:00
tags:
  - agents
  - computer-use
  - gui-agents
  - benchmarks
  - mcp
featured: false
draft: false
---

Sometime this month the headline number flipped. On [OSWorld-Verified](https://benchlm.ai/benchmarks/osWorldVerified) — the benchmark that has defined "can an agent drive a real desktop" for the last year — the top models now sit at 85%, above the roughly 72% human baseline the original OSWorld authors measured. As of the June 27 leaderboard the frontier is clustered within 1.6 points, which is the polite way of saying the benchmark is saturating. Stanford's AI Index tells the same story longitudinally: agent success on OSWorld went from 12% to about 66% across 2025 into early 2026, and the curve hasn't flattened so much as run out of headroom.

That is a real milestone. It is also the least interesting thing about computer-use agents right now. The number crossed human parity at almost the exact moment it stopped being the question worth asking. Two things underneath it matter more: how the benchmark got trustworthy enough to believe, and what the agents are actually *doing* to win — which turns out to be the wrong thing more often than you'd hope.

## The score moved because the harness did

It's tempting to read 12% → 85% as pure model capability. A lot of it isn't. The original OSWorld shipped in mid-2025 and was, by its own maintainers' later admission, a leaky measuring stick. The [OSWorld-Verified rebuild](https://xlang.ai/blog/osworld-verified) catalogs the rot: websites added CAPTCHAs and anti-crawling defenses that broke evaluation functions, task instructions were ambiguous ("purple background" had several defensible answers), and brittle temporal dependencies meant a task could fail on setup rather than on the agent. The team worked through 300-plus reported issues, migrated the execution substrate from VMware to AWS, and parallelized hard enough to take a full evaluation from ten-plus hours down to minutes.

That last detail is the one builders should sit with. A meaningful share of the "progress" in GUI agents over the past year is eval and harness engineering, not weights. You cannot tune a policy against a benchmark that takes ten hours and randomly fails on infrastructure; the moment the loop got fast and deterministic, the scores moved. This is the same lesson the [coding-agent world already absorbed](/posts/the-harness-got-a-name/) — the harness is a first-class component, not plumbing — arriving on the desktop a few months late.

The flip side is a caveat worth keeping. A real-desktop training shop [argues bluntly](https://coasty.ai/blog/osworld-benchmark-2026-results-ai-computer-use) that most agents are trained against synthetic environments and APIs and "never actually see a real desktop," and that a benchmark score earned in a clean VM doesn't transfer to the messy machine in front of a user. Saturation on OSWorld-Verified is a ceiling on a curated 369-task set, not a claim about your accounting software's modal dialog. Treat the 85% the way you'd treat a SWE-bench number: necessary, not sufficient.

## They win by clicking — and that's the bug

Here's the result that reframes the whole field. [OSWorld-MCP](https://openreview.net/forum?id=rceD6wwt4B) takes the same desktop tasks and gives the agent a second option alongside the mouse: 158 validated tools, exposed over MCP, spanning seven common applications. The question it asks is no longer "can the agent click the right pixels" but "given a typed API *and* a GUI, does the agent pick the better action?"

The capability lift is large when tools get used. OpenAI o3 roughly doubles, from 8.3% to 17.6% at a 15-step budget; Claude 4 Sonnet goes from 38.9% to 45.0% at 50 steps. But the headline finding is the gap between *available* and *used*: even state-of-the-art models invoke a tool only about a third of the time. Two out of three opportunities, the agent reaches for the cursor when a deterministic function call was sitting right there.

If you've shipped any agent, that should feel familiar. A GUI click is high-variance — it depends on rendering, layout, timing, and the model's visual grounding holding up under a screenshot. An MCP tool call is low-variance — it either returns or errors, and you can log it, retry it, and unit-test it. The agent that prefers clicking is choosing the fragile path when the robust one exists. The headline OSWorld-Verified number rewards *finishing the task*; it does not penalize *winning the unreliable way*. So the leaderboard saturates while the action-selection problem stays wide open.

This is the desktop instance of a thesis this blog keeps returning to: [code — and structured tool calls — should be the action space](/posts/code-is-the-action-space-now/), not pixel coordinates. Computer use was supposed to be the fallback for systems with no API. What OSWorld-MCP shows is that even when an API exists, current agents under-use it, which means the practical engineering win for the next year isn't a better clicker. It's a router: a policy that defaults to the typed action and treats the GUI as the escape hatch, plus training signal that actually rewards that preference.

## What this means if you're building one

A few concrete takeaways from the month:

- **Don't buy the 85% as a product claim.** It's a saturating score on a curated, cleaned-up set. Build your own small eval against *your* applications, on real machines, and expect the gap to be ugly.
- **Instrument the click-vs-call decision.** If your agent has MCP tools and a GUI fallback, log which it chose per step and what the variance was. A 33% tool-invocation rate is a measurable, fixable defect, not a law of nature.
- **Spend on the harness, not just the model.** Fast, deterministic, parallel evaluation is what made the scores move. The same investment is what will make your agent debuggable.
- **Watch the open lifecycle stacks.** Frameworks like [ClawGUI](https://github.com/zju-real/ClawGUI) now bundle online RL training, standardized eval, and real-device deployment, which is the shape of how small specialized GUI agents will actually get built and shipped.

Computer-use agents passing the human baseline is the kind of milestone that makes a good press release and a misleading roadmap. The real frontier moved underneath it: from "can it operate the screen" to "does it choose the reliable action when both are available." On current evidence, it doesn't — yet.

## Worth bookmarking

- [OSWorld-Verified leaderboard](https://benchlm.ai/benchmarks/osWorldVerified) — the saturating frontier, updated continuously.
- [XLANG: Introducing OSWorld-Verified](https://xlang.ai/blog/osworld-verified) — how the benchmark got rebuilt and why it matters.
- [OSWorld-MCP (OpenReview)](https://openreview.net/forum?id=rceD6wwt4B) — the click-vs-call benchmark and the 33% tool-invocation finding.
- [Coasty: OSWorld 2026 results](https://coasty.ai/blog/osworld-benchmark-2026-results-ai-computer-use) — the real-desktop vs synthetic-environment critique.
- [ClawGUI](https://github.com/zju-real/ClawGUI) — a full-lifecycle open-source stack for training and deploying GUI agents.
- [OSU GUI Agents Paper List](https://github.com/OSU-NLP-Group/GUI-Agents-Paper-List) — the running bibliography for this whole subfield.
