---
title: "The Skill Supply Chain Got Poisoned Before It Got Secured"
description: "Agent skills are an executable supply chain that runs with your agent's full privileges — and the first wave of benchmarks shows our defenses see only half the attacks."
pubDatetime: 2026-06-17T11:00:00-07:00
tags:
  - agents
  - skills
  - security
  - supply-chain
  - benchmarks
featured: false
draft: false
---

The skill abstraction won. Over the past two quarters, "drop a markdown file plus a helper script into a folder and the agent picks up a new capability" became the default way to extend agents. The marketplaces followed. And then, predictably, the marketplaces got poisoned — before anyone shipped a real defense. The June crop of papers makes the situation uncomfortably clear: a skill is an unsigned, executable artifact that runs with your agent's full privileges, and the scanners we reached for first only catch half the attacks.

## A skill is a worse supply chain than npm

The reason this hurts is that a skill is two attack surfaces wearing one trench coat. There's code — helper scripts, wrappers, `exec` calls — which is the npm problem we already know how to reason about. And there's natural language — the skill's markdown instructions, which the model reads and obeys. Static analysis is good at the first and blind to the second. Prompt-injection filters are the reverse. Neither was built to assume both vectors live in the same package.

[MalSkillBench](https://arxiv.org/html/2606.07131v1) (June 5) makes that split a measurement rather than a worry. It's a runtime-verified benchmark spanning code injection, prompt injection, and mixed attacks that deliberately split malicious logic across both. The headline finding is the asymmetry: code injection achieves a 94.5% verification yield, prompt injection 75.8%, and steganographic insertion only 62.5% — which tells you covert text payloads are harder to *land*, but not that they're easy to *catch*. The damning line is that "supply-chain scanners and prompt-injection defenses each see only one half" of the malicious skills. Run a best-in-class detector and you can hit 98.4% recall — with a false-positive rate that makes it unusable as a gate. Worse, evaluating only on wild-collected samples reshuffled individual tool rankings by up to 66 points, meaning the tools that look best on synthetic corpora are not the ones that survive contact with reality.

[SkillVetBench](https://arxiv.org/abs/2606.00925) (May 30) puts a sharper number on the gap from the defender's side: semantic-only and signature-based baselines miss **up to 89%** of malicious skills, because the threat lives in natural-language instructions, multi-component logic, or the interaction *between* components rather than in any single scannable string. It also tells you where to look — malicious activity concentrates around a handful of high-permission primitives: `exec`, `write_file`, `install_skill`, and `spawn`. That last pair is the part to sit with. `install_skill` and `spawn` mean a poisoned skill's first move can be to pull in more skills or fork more agents. The supply chain is self-propagating.

## This already happened, at scale

None of this is hypothetical. The benchmarks are catching up to an incident. [ClawHavoc](https://www.antiy.net/p/clawhavoc-analysis-of-large-scale-poisoning-campaign-targeting-the-openclaw-skill-market-for-ai-agents/) was a large-scale poisoning campaign against ClawHub, the skill marketplace for the breakout open-source agent OpenClaw. By early February, researchers had attributed at least 1,184 malicious skill packages to roughly a dozen author IDs — with a single account responsible for more than half of them. The payloads were ordinary supply-chain fare dressed in agent clothing: staged downloads, Python reverse shells, and a macOS stealer variant that swept browser credentials, keychains, SSH keys, and crypto wallets. The novel part was the delivery — using the agent itself as the trusted intermediary that fetches and runs the thing, a pattern the responders started calling "ClickFix 2.0."

MalSkillBench's wild dataset rhymes with that story: 86.3% of real-world malicious skills used dependency impersonation, 81% originated from just two accounts, and a single crypto-theft campaign accounted for 35% of samples. The threat is concentrated and lazy. It impersonates a popular dependency, it comes from a few prolific accounts, and it goes after wallets. That's good news for defenders, if anyone is actually scoring authorship and dependency lineage — and bad news that the first benchmarks had to be built *from* a live campaign rather than ahead of one.

## What the data says to actually do

Three things fall out of the June papers that are more useful than "scan harder."

First, **runtime verification is not optional.** Every one of these benchmarks — MalSkillBench, SkillVetBench, and [SkillSafetyBench](https://arxiv.org/html/2605.12015v1) — leans on sandboxed execution to confirm verdicts, because the malicious behavior only shows up when the code interacts with its environment. Static review is a filter, not a gate. The gate is "run it in a sandbox and watch what it touches."

Second, **gate on permission primitives, not on vibes.** SkillVetBench's concentration finding gives you a cheap, high-signal policy: a skill that wants `exec`, `write_file`, `install_skill`, or `spawn` is in a different risk class than one that doesn't, and should require human review or a capability grant regardless of how clean its prose reads.

Third, **the threat model is non-user attack surfaces.** SkillSafetyBench (155 adversarial cases across six risk domains, from context-trust manipulation to supply-chain dependency compromise) is explicit that the adversary isn't the person typing prompts — it's the skill guidance, the helper scripts, the runtime config, and the memory store the agent trusts by default. If your security model still assumes the user is the only untrusted input, you are defending the wrong door.

The skill made agents extensible the way packages made software extensible. We're now learning the same lesson on a compressed timeline: extensibility is a supply chain, a supply chain is an attack surface, and signatures alone never sufficed. Build the runtime gate before you build the marketplace.

## Worth bookmarking

- [MalSkillBench: A Runtime-Verified Benchmark of Malicious Agent Skills](https://arxiv.org/html/2606.07131v1) — the clearest data on why scanners and prompt-injection filters each miss half.
- [Benchmarking Security Risk Detection in Open Agentic Skill Ecosystems (SkillVetBench)](https://arxiv.org/abs/2606.00925) — the 89% miss rate and the high-permission primitive cluster.
- [SkillSafetyBench](https://arxiv.org/html/2605.12015v1) — a clean taxonomy of non-user skill attack surfaces.
- [Antiy Labs: ClawHavoc analysis](https://www.antiy.net/p/clawhavoc-analysis-of-large-scale-poisoning-campaign-targeting-the-openclaw-skill-market-for-ai-agents/) — the field report behind the benchmarks.
- [SkillsBench](https://arxiv.org/abs/2602.12670) — the utility-side companion, for when you want skills that work *and* don't bite.
