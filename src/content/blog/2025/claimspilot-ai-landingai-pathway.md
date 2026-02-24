---
title: "3rd Place — ClaimsPilot AI at LandingAI x Pathway Hackathon"
description: "Built ClaimsPilot AI — automating claim intake, triage, and routing with real-time visibility and evidence links. My first hack in the financial domain."
pubDatetime: 2025-08-15T00:00:00Z
tags:
  - hackathon
  - ai
  - fintech
  - automation
featured: false
heroImage: "/images/claimspilot-landingai.jpg"
---

My first hackathon in the financial domain — and it connected directly to my day job at Guidewire, where I build AI systems for insurance workflows. ClaimsPilot AI took that production experience and distilled it into a focused prototype.

## The Problem

Insurance claims processing is one of the most labor-intensive workflows in financial services. Adjusters manually review submissions, classify damage types, cross-reference policy details, and route claims to specialized teams. A single claim can touch 5-8 people before resolution. The result: slow turnaround, inconsistent triage, and frustrated policyholders.

## What We Built

**ClaimsPilot AI** — an end-to-end claims automation system that handles intake, triage, routing, and tracking with AI at every step.

### Architecture

The system operates as a pipeline of specialized processing stages:

1. **Document Ingestion** — LandingAI's computer vision models extract structured data from claim photos, receipts, police reports, and medical documents. OCR handles text extraction while object detection identifies damage types from images.

2. **Entity Extraction & Normalization** — An LLM-based extraction layer pulls key entities: claimant info, incident details, damage descriptions, dates, and amounts. These are normalized against the policy schema for downstream processing.

3. **Triage Engine** — A classification model assigns severity (low/medium/high/critical) and claim type (property, auto, medical, liability) based on extracted features. The model uses a combination of rule-based filters for regulatory requirements and ML classification for nuanced cases.

4. **Smart Routing** — Claims are routed to handlers based on a scoring algorithm that considers: handler expertise match, current workload, claim complexity, and SLA requirements. The routing optimizes for both speed and quality of resolution.

5. **Real-Time Pipeline** — Pathway's streaming framework connects all stages into a live pipeline. New claims flow through the system in seconds, and status updates propagate to the dashboard in real-time via WebSocket connections.

### Technical Stack

- **Computer Vision** — LandingAI for document and damage image analysis
- **Data Streaming** — Pathway for real-time event-driven processing
- **Backend** — Python FastAPI with async handlers for concurrent claim processing
- **LLM Layer** — GPT-4 for entity extraction, summarization, and natural language claim descriptions
- **Frontend** — React dashboard with real-time claim status tracking, filterable queue views, and evidence galleries
- **Storage** — PostgreSQL with pgvector for similarity search across historical claims

### Key Capabilities

- **Automated Claim Intake** — Submit a claim with photos and documents; AI extracts everything in seconds
- **Intelligent Triage** — Classifies severity and type with 92% accuracy on test data, flagging edge cases for human review
- **Evidence Linking** — Automatically associates photos, documents, and extracted data points to build a complete claim file
- **Real-Time Dashboard** — Live queue with filters by status, severity, handler, and SLA countdown
- **Similarity Search** — Finds historically similar claims using vector embeddings to assist adjusters with precedent-based decisions

## Why This Matters

From my work at Guidewire, I've seen how claims automation directly impacts policyholder experience and operational costs. The average claim takes days to route to the right handler. ClaimsPilot AI reduces that to seconds with consistent accuracy and full audit trails.

The combination of LandingAI's vision capabilities with Pathway's streaming framework was particularly powerful — it meant we could process document-heavy claims in real-time rather than batch, which is a common bottleneck in production claims systems.

## Key Takeaways

- **Domain Knowledge is an Edge** — My insurance industry experience at Guidewire gave our solution a practical grounding that pure-tech approaches often miss
- **Vision + NLP Fusion** — Combining computer vision for document/image analysis with LLM-based entity extraction creates a much richer understanding of claims than either alone
- **Streaming Over Batch** — Real-time processing with Pathway transformed the user experience from "submit and wait" to "submit and watch it flow"
- **Production Patterns at Hackathon Speed** — Applying patterns I use in production (routing algorithms, SLA tracking, audit trails) gave the prototype immediate credibility with judges
