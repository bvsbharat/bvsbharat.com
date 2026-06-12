---
title: "Skills Are the New SDK"
description: "OpenAI killed its visual Agent Builder the same week Google shipped first-party skills. The agent capability layer just consolidated."
pubDatetime: 2026-06-12T11:00:00-07:00
tags:
  - agents
  - skills
  - platforms
  - ecosystem
  - developer-experience
featured: false
draft: false
---

Two announcements eight days apart just settled a question the agent ecosystem has been circling for a year: how do you package what an agent knows how to do? On June 3, OpenAI announced it is [winding down Agent Builder and Evals](https://developers.openai.com/api/docs/deprecations), the visual workflow canvas it launched with [AgentKit](https://openai.com/index/introducing-agentkit/) barely eight months ago, with a final shutdown on November 30, 2026. On June 10, Google publicly launched [google/skills](https://github.com/google/skills), a first-party repository of Agent Skills for Gemini, BigQuery, Cloud Run, GKE, Firebase, and the rest of its cloud portfolio, installable into any compatible agent with one `npx skills add google/skills` command.

One vendor retired a proprietary builder. Another shipped its product knowledge as portable markdown. These are the same event viewed from opposite ends: the capability layer for agents has consolidated around skills and code, and the visual middle layer is gone.

## The middle layer collapsed

What's telling about the Agent Builder sunset isn't that OpenAI killed a product — it's where it tells users to go. The migration paths are the Agents SDK "for workflows that should continue as code" and Workspace Agents in ChatGPT for use cases better suited to natural language. Code on one side, plain English on the other. Nothing in between survived.

The drag-and-drop canvas was supposed to be the accessible middle: more controllable than a chat prompt, less intimidating than a codebase. In practice it inherited the worst of both. Visual workflows are still programs — they have control flow, state, and failure modes — but you debug them through a GUI instead of a debugger, version them through screenshots instead of git, and test them through clicking instead of CI. Meanwhile the models got good enough that the natural-language end ("just tell the agent what you want") absorbed the easy use cases, and OpenAI's own [Agents SDK grew sandboxing and a full model harness](https://devops.com/openai-upgrades-its-agents-sdk-with-sandboxing-and-a-new-model-harness/) in April — instructions, tools, approvals, tracing, handoffs, resume bookkeeping — absorbing the hard ones. The canvas had no remaining constituency.

If you bet a production workflow on a visual agent builder — OpenAI's or anyone's — the lesson generalizes: the artifact you author should be one you can diff, test, and carry to another runtime. Which is exactly what won.

## First-party skill packs are the new vendor SDK

The [Agent Skills specification](https://agentskills.io/home) — a folder with a `SKILL.md`, YAML frontmatter, markdown instructions, optional scripts — was published by Anthropic in December 2025, and [adopted with unusual speed](https://thenewstack.io/agent-skills-anthropics-next-bid-to-define-ai-standards/) by OpenAI, Microsoft, Google, JetBrains, and dozens of other clients within months. What's new in June is the second-order effect: platform vendors are now shipping *first-party* skill packs as a primary developer surface.

Look at what's actually in google/skills. Alongside service basics (BigQuery, Cloud SQL, AlloyDB) there are opinionated "recipes" for onboarding and authentication, the entire Well-Architected Framework restated as agent-consumable guidance, and — most interesting — a skill for a **Skill Registry API on Agent Platform**. Google isn't just publishing skills; it's building managed infrastructure for distributing them inside organizations. Flutter and Dart have their [own](https://github.com/flutter/skills) [repos](https://github.com/dart-lang/skills). The pattern is unmistakable: documentation teams used to write docs for humans and SDKs for programs; now there's a third artifact, written for agents, and vendors are treating it as load-bearing.

This is a real shift in how product knowledge reaches developers. When your cloud provider's best practices ship as a skill, the agent applies them at the moment of action — provisioning the cluster, writing the Terraform — rather than depending on whether a human read the docs. The vendor's incentive is obvious: an agent with your skill pack installed makes fewer mistakes on your platform, files fewer support tickets, and churns less.

## The npm moment is coming, and the registry knows it

Vercel's [skills.sh](https://skills.sh/) registry now tracks hundreds of thousands of published skills, and the most popular entries count installs in the millions. Anyone who lived through npm's adolescence should feel a familiar chill. Skills are instructions an agent follows with whatever permissions it holds. A malicious or subtly poisoned skill is a prompt-injection payload with a distribution channel, and today's ecosystem has no signing, no provenance attestation, and no meaningful review gate — just install counts as a trust proxy.

That's the context that makes Google's Skill Registry API more than a convenience feature. Enterprises are not going to let agents pull arbitrary instructions from a public leaderboard, for the same reason they don't let CI pull from unvetted package registries. Private registries, allowlists, and curation pipelines for skills are about to become a product category. The open question is whether the ecosystem gets provenance standards before its left-pad incident or after. History suggests after.

The practical takeaways for anyone building agents this quarter: author capabilities as skills against the open spec, not against any single platform's builder — the spec has survived a vendor product that didn't. Treat your skills directory like a dependency manifest, because that's what it is — review what goes in, pin what you trust. And if you're a platform or library maintainer, your agent-facing skill pack is no longer optional; Google just made it table stakes.

## Worth bookmarking

- [google/skills](https://github.com/google/skills) — Google's first-party Agent Skills for Cloud, Gemini, and the Agent Platform registry
- [Agent Skills specification](https://agentskills.io/home) — the open standard: format, progressive disclosure, client showcase
- [skills.sh](https://skills.sh/) — Vercel's skill registry and leaderboard; useful for gauging what the ecosystem actually installs
- [OpenAI deprecations page](https://developers.openai.com/api/docs/deprecations) — the Agent Builder/Evals wind-down timeline and migration paths
- [anthropics/skills](https://github.com/anthropics/skills) — Anthropic's reference skills, worth reading as the canonical style guide
- [The New Stack on Agent Skills as a standards play](https://thenewstack.io/agent-skills-anthropics-next-bid-to-define-ai-standards/) — good background on how the spec spread
