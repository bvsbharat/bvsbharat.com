---
title: "Agents Are Writing Their Own Skills — and Retrieval Is the New Bottleneck"
description: "May 2026's skill-library research shows agents can now accumulate reusable capabilities, but retrieving and adopting them is harder than generating them."
pubDatetime: 2026-06-02T11:00:00-07:00
tags:
  - agents
  - skill-libraries
  - continual-learning
  - evals
  - retrieval
featured: false
draft: false
---

The interesting question about agents this month stopped being "can the model do the task" and became "can the agent keep the thing it figured out." A cluster of papers from the last two weeks of May 2026 all converge on the same architecture: agents that distill their own runs into reusable skills, store them in a growing library, and pull them back in on later tasks. The generation side is basically solved. What is not solved — and what the newest benchmarks make uncomfortably clear — is retrieval, adoption, and trust.

This matters because it moves the center of gravity of agent design. For two years the lever was the prompt: what you put in the context window. The skill-library turn says the lever is the *accumulated asset*: what the agent has learned to do across thousands of prior runs. That is a different engineering problem, and it has different failure modes.

## Skills are becoming code, not prose

The clearest shift is in how a skill is represented. The early lineage here — [AutoSkill](https://arxiv.org/html/2603.01145v1), [MemSkill](https://arxiv.org/abs/2602.02474), and [ProcMEM](https://arxiv.org/pdf/2602.01869) from February and March — mostly treated a skill as distilled natural-language heuristics: a paragraph reminding the agent how it succeeded last time. That works at small scale and degrades fast, because prose skills are unverifiable and the model is free to ignore them.

[HASP: Harnessing LLM Agents with Skill Programs](https://arxiv.org/html/2605.17734v1) (May 18) pushes the opposite way. It compiles experience into executable Python "Program Functions," each with a `should_activate()` guard and an `intervene()` body that either rewrites the agent's action or injects corrective context mid-reasoning. The gap between the two representations is not subtle: PF-only intervention hits 51.0% on web-search reasoning against 20.5% for prompt-only skills, and climbs to the 60s on coding with a teacher in the loop. The lesson is the same one we keep relearning in agent infra — anything you can make executable and checkable beats anything you leave as advice. A skill that runs is a skill you can test; a skill that's a paragraph is a suggestion.

## The library has structure now

Once skills become first-class objects, the next question is how they relate. [SkillGraph](https://arxiv.org/html/2605.12039v1) (May 12) drops the flat list and models skills as nodes in a directed graph, with typed edges for prerequisite, enhancement, and co-occurrence relations. Instead of retrieving one skill by embedding similarity, it retrieves an *ordered subgraph* that maps to a multi-step plan, then updates the graph from RL feedback so the library and the policy improve together. The reported gains are largest exactly where you'd expect — complex tasks that require composing several skills in the right order, on ALFWorld, WebShop, and search-augmented QA.

This is the part worth sitting with. A flat skill store assumes capabilities are independent. They aren't. "Authenticate to the API" is a prerequisite for "paginate the results," which enhances "summarize the dataset." Encoding those dependencies is what turns a pile of snippets into something an agent can plan over.

## The wall: retrieval, timing, and adoption

Here's where the optimism gets checked. [Skill Retrieval Augmentation (SRA)](https://arxiv.org/abs/2604.24594), revised May 21, names the scaling problem bluntly: the common pattern of enumerating every available skill in the context window collapses as libraries grow. Its SRA-Bench (5,400 instances, 26,262 skills) shows the real bottleneck isn't fetching the right skill from a big corpus — it's the agent *knowing it needs one at all*. "When to retrieve" turns out to be harder than "what to retrieve," and it's a decision current agents make badly.

[SkillLearnBench](https://arxiv.org/html/2604.20087) (April 22), the first benchmark for continual skill learning, is the sobering capstone. Four findings every team building this should internalize:

- **Generated skills still trail human-authored ones badly.** The best method closes only about 45% of the gap between no-skill and human-authored baselines.
- **Self-feedback drifts.** Refining skills from the agent's own judgment produces "recursive drift rather than progress." Genuine improvement needs an external signal — a teacher, a verifier, a real outcome.
- **Bigger isn't better at authoring.** Stronger LLMs don't reliably write better skills; mid-tier models often win by balancing specificity against flexibility.
- **Availability is not adoption.** A correct skill sitting in the library does nothing if the solving agent declines to use it. "Whether the agent adopts the skill" matters more than "what the skill contains."

That last point is the quiet killer. We've spent the research budget on generation and storage; the act of *trusting and invoking* a learned skill at the right moment is under-engineered. It's the same failure surface as tool selection at scale, just one level up.

## What this means in practice

If you're building agents that learn, three things follow. First, make skills executable and gated — a `should_activate()` predicate is worth more than a better description. Second, model dependencies explicitly; a graph beats a list the moment tasks need composition. Third, do not trust the agent to self-grade its own skills — wire in external verification, because self-feedback loops drift toward confident nonsense. And benchmark adoption, not just generation: a skill the agent won't call is a skill you don't have.

The skill-library turn is real and it's the most promising path to agents that get better with use rather than plateauing. But the May results are a reminder that "self-improving" is still mostly aspirational. The improvement loop closes only when there's a verifier in it.

## Worth bookmarking

- [SkillGraph: Skill-Augmented RL via Evolving Skill Graphs](https://arxiv.org/html/2605.12039v1) — graph-structured skill libraries, retrieves ordered subgraphs.
- [HASP: Harnessing LLM Agents with Skill Programs](https://arxiv.org/html/2605.17734v1) — skills as executable Program Functions, not prose.
- [Skill Retrieval Augmentation for Agentic AI](https://arxiv.org/abs/2604.24594) — SRA-Bench and the "when to retrieve" problem.
- [SkillLearnBench](https://arxiv.org/html/2604.20087) — the first continual-skill-learning benchmark, and a reality check.
- [AutoSkill](https://arxiv.org/html/2603.01145v1) / [MemSkill](https://arxiv.org/abs/2602.02474) — the natural-language skill-distillation lineage these papers build on.
- [VoltAgent/awesome-ai-agent-papers](https://github.com/VoltAgent/awesome-ai-agent-papers) — tracking the 2026 agent-research firehose.
