---
title: "Data Agents: The Hard Part Was Never the SQL"
description: "Anthropic and OpenAI independently shipped internal data agents and reached the same conclusion: discovery beats generation, and structure beats access."
pubDatetime: 2026-06-08T11:00:00-07:00
tags:
  - agents
  - data-agents
  - context-engineering
  - text-to-sql
  - retrieval
featured: false
draft: false
---

If you are building an agent that answers questions over a data warehouse, the model writing the SQL is not your problem. Two frontier labs just published production postmortems that say so explicitly, and the research literature has been quietly converging on the same point for months. The bottleneck is finding the right tables, disambiguating what a business question actually means, and keeping the agent's context fresh. The query itself is the easy 5%.

This is worth dwelling on because it inverts how most teams scope the work. People reach for a better model and a bigger context window. The labs that have shipped this for thousands of internal users reached for a semantic layer and a git repo.

## Two labs, one conclusion

[OpenAI's in-house data agent](https://openai.com/index/inside-our-in-house-data-agent/) reasons over 600+ petabytes across roughly 70,000 datasets, serving thousands of employees through Slack, a web UI, IDEs, and the Codex CLI over MCP. Their framing is blunt: the challenge "isn't writing SQL — it's finding the right tables." Their answer is six offline-assembled context layers retrieved at runtime — table usage patterns mined from historical queries, human annotations of business meaning, Codex-extracted meaning from pipeline code, institutional knowledge scraped from Slack/Docs/Notion, a correction memory, and live runtime queries against the warehouse.

[Anthropic's self-service analytics agent](https://claude.com/blog/how-anthropic-enables-self-service-data-analytics-with-claude), published in June, takes a different shape — a set of Markdown *skills* loaded into Claude Code rather than a standalone runtime — but lands in the same place. They name the central failure mode precisely: *concept-to-entity ambiguity*. Defining "active users" means deciding which actions count, whether to exclude fraudulent accounts, and what lookback window applies. With hundreds of plausible fields in the data model, the agent cannot pick the right ones on vibes. The numbers are stark: without skills, accuracy on their evals didn't exceed 21%; with a curated semantic layer and procedural skills, it sits consistently above 95%. The good [comparison writeup from DataChain](https://datachain.ai/blog/openai-anthropic-data-agents) is worth reading if you want the two architectures side by side.

## Structure beats access — and it kills naive RAG

The single most useful finding is an ablation, not an architecture. Anthropic gave the agent full-text search over thousands of historical SQL queries from real dashboards and notebooks — the obvious "let RAG figure it out" move. They confirmed it read the files. Accuracy moved by *less than a point*.

Sit with that. Unrestricted retrieval over a pile of correct precedent did almost nothing, because the agent couldn't reliably map a new question to the relevant prior. What worked instead was a *governed semantic layer*: curated metric and dimension definitions the agent is structurally required to consult first. Structure, not access.

This is the part most teams will get wrong. The default instinct — embed every table comment and old query, stuff the top-k into context — is precisely the approach that barely registered in the ablation. Curation is the work. You are not building a retriever; you are building a map.

## The research has been saying this too

The academic side has spent the last few months formalizing the same problem under the name *schema linking*. New enterprise benchmarks like BIRD-Ent and Spider-Ent deliberately model the hard case — 4,000+ columns, abbreviated domain-specific names, and knowledge scattered across ~1.5M tokens of documentation — because the older single-database benchmarks were saturated and unrealistic. On those harder scopes, the wins come from retrieval, not generation. [AutoLink](https://arxiv.org/html/2511.17190) reports a 27% jump in strict recall on Spider 2.0-Lite while cutting token consumption by 88%, by treating schema discovery as an autonomous exploration loop rather than a one-shot vector lookup. [RASL](https://assets.amazon.science/1b/95/8f62e89647348f4c4836f6c3040d/rasl-retrieval-augmented-schema-linking-for-massive-database-text-to-sql.pdf) and [LinkAlign](https://arxiv.org/html/2503.18596v4) attack the same massive-schema retrieval problem from different angles. The production postmortems and the papers are describing one phenomenon from two vantage points.

## Keeping the map fresh, and trusting the answer

Two operational details separate the working systems from the demos. First, **freshness through colocation**. Anthropic keeps modeling code, semantic-layer definitions, reference docs, and dashboard definitions in a single repo, so a pull request that changes a model is forced to touch the docs that describe it. Documentation drift is the slow death of every data catalog; colocation makes the docs a build dependency rather than a good intention. OpenAI's Codex-enrichment layer attacks the same staleness problem by deriving meaning from pipeline code directly.

Second, **verification as a first-class layer**. Anthropic runs an adversarial sub-agent that challenges the primary agent's assumptions — worth a 6% accuracy gain at a 32% token premium — and stamps every answer with a provenance footer: source tier, freshness, and ownership. For analytics, a confidently wrong number is worse than no number, so the agent has to show its work. This echoes the broader 2026 theme that verification is becoming the substrate agents run on, not a bolt-on.

The takeaway for builders is unglamorous and freeing. If your data agent underperforms, the fix is probably not a frontier model swap or a longer context window. It is a semantic layer, curated reference docs colocated with your transformations, an eval set built from real dashboards, and a verification pass that cites its sources. That is context engineering, and it is where the accuracy actually lives.

## Worth bookmarking

- [How Anthropic enables self-service data analytics with Claude](https://claude.com/blog/how-anthropic-enables-self-service-data-analytics-with-claude) — the 21%→95% skills story and the full-text-search ablation
- [Inside OpenAI's in-house data agent](https://openai.com/index/inside-our-in-house-data-agent/) — the six context layers, in detail
- [We read OpenAI's and Anthropic's data-agent posts so you don't have to](https://datachain.ai/blog/openai-anthropic-data-agents) — clean side-by-side comparison
- [AutoLink: Autonomous Schema Exploration for Scalable Schema Linking](https://arxiv.org/html/2511.17190) — discovery-as-exploration for massive schemas
- [RASL: Retrieval Augmented Schema Linking for Massive Database Text-to-SQL](https://assets.amazon.science/1b/95/8f62e89647348f4c4836f6c3040d/rasl-retrieval-augmented-schema-linking-for-massive-database-text-to-sql.pdf) — the research mirror of the labs' findings
