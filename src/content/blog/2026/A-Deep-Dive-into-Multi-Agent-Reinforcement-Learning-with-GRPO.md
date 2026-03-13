---
title: "Training a Virtual Company: A Deep Dive into Multi-Agent Reinforcement Learning with OpenEnv & Unsloth"
description: "How exploring LLM fine-tuning led to building a Gymnasium-compatible RL environment where 7 LLM-powered agents run a company — trained with GRPO + LoRA on Qwen 2.5 14B — and what we learned about reward design, emergent collaboration, and the future of agentic AI."
pubDatetime: 2026-03-07T00:00:00Z
tags:
  - openenv
  - agents
  - rl
  - unsloth
  - grpo
  - lora
  - qwen
  - python
  - gymnasium
featured: true
heroImage: "https://www.youtube.com/watch?v=0i6xT683rMI"
---

## The Spark: Why RL Became the Next Obsession

It started with a deep dive into how LLM fine-tuning actually works. Not the API calls — the mechanics underneath. The more I studied techniques like RLHF and GRPO, the more a pattern emerged: if you truly want to understand how models learn and improve, you need to understand reinforcement learning at a fundamental level.

The core idea of RL is deceptively simple: increase the chance of seeing "good" outcomes, decrease the chance of seeing "bad" outcomes. But the intricacies — what "good" and "bad" mean, how you quantify it, how you update policies across multiple agents with competing objectives — that's where the real engineering lives.

Understanding GRPO specifically gave me deep intuition into *why* RL is so effective for fine-tuning. Unlike PPO, which requires four models in memory (policy, reference, critic, reward model), GRPO eliminates both the critic and the reward model entirely. It samples the LLM multiple times, computes rewards for each response, Z-score normalizes them within the group, and uses those normalized advantages to update the policy. This makes it dramatically more memory-efficient and simpler to train. As Unsloth's documentation puts it — the trick of RL is you need only two things: a question, and a reward function to verify the output. With those two ingredients, you can train any model to reason.

That curiosity pulled me deeper: into RL environments, into how you create worlds where agents observe, act, receive feedback, and get better over time. And eventually, it led to a question that became a project:

**What if you trained not just one agent, but an entire team of agents to run a startup together?**

That project became **O2 OpenOffice** — our submission for the **OpenEnv Hackathon 2026**, hosted by Meta PyTorch, Hugging Face, and Cerebral Valley. A $100K+ prize pool hackathon where participants built RL environments and post-trained base models across 5 challenge themes.

---

## The Context: Why Multi-Agent RL Matters Right Now

Just days before our hackathon, RevenueCat posted what might be the first-ever job listing for an AI agent — an "Agentic AI Developer Advocate" role paying $10,000/month for six months. The role is designed for an autonomous AI system that creates content, runs growth experiments, and provides product feedback. A human operator manages the agent, but the agent does the work. The role comes with KPIs: at least two pieces of technical content per week, 50+ meaningful community interactions, weekly growth experiments, and structured feature requests to the engineering team.

This isn't a thought experiment anymore. Companies are treating AI agents as team members with budgets, KPIs, and performance expectations. The question is no longer *whether* agents will take on organizational roles — it's *how well they coordinate when multiple agents work together.*

---

## What is OpenEnv? The Framework Behind It All

Before diving into our project, it's worth understanding the framework we built on.

**OpenEnv** is an end-to-end framework by **Meta PyTorch** for creating, deploying, and using isolated execution environments for **agentic RL post-training**. Think of it as Gymnasium, but purpose-built for training LLMs via RL rather than traditional RL agents.

**The problem it solves**: Standard Gymnasium was designed for classic RL — Atari, MuJoCo, CartPole — with numeric observation and action spaces. But agentic LLM RL training needs something different: environments that are complex, stateful, long-running, communicate via structured text, and can run in isolated containers over networks. OpenEnv standardizes this so framework authors (TRL, Unsloth, SkyRL) and environment creators can interoperate.

### The OpenEnv API vs Gymnasium

| Aspect | Gymnasium | OpenEnv |
|--------|-----------|---------|
| **Target** | Classic RL agents (numeric actions/observations) | LLM agentic RL post-training (structured text) |
| **Communication** | In-process Python calls | WebSocket over network (client-server) |
| **Isolation** | Environments run in-process | Docker containers, Kubernetes, HF Spaces |
| **Types** | `np.ndarray` spaces (Box, Discrete) | Pydantic models (type-safe, serializable) |
| **API** | `step()` returns `(obs, reward, terminated, truncated, info)` | `step()` returns `Observation` with `done` and `reward` embedded |
| **State** | No standard `state()` method | `state()` is first-class (episode_id, step_count) |
| **Async** | Sync only | Async-first with sync wrapper via `.sync()` |
| **Scaling** | Single process | Up to ~16,384 concurrent sessions (multi-node) |

The core interface looks like this:

```python
class Environment(ABC, Generic[ActT, ObsT, StateT]):
    @abstractmethod
    def reset(self, seed=None, episode_id=None, **kwargs) -> ObsT: ...

    @abstractmethod
    def step(self, action: ActT, timeout_s=None, **kwargs) -> ObsT: ...

    @property
    @abstractmethod
    def state(self) -> StateT: ...
```

Actions and Observations are Pydantic models — type-safe and serializable — rather than numpy arrays. This is essential for LLM agents that produce and consume structured JSON, not floating point vectors.

### The OpenEnv Ecosystem

OpenEnv integrates with the major RL training frameworks:

- **TRL** (Hugging Face) — official integration for GRPO training
- **Unsloth** — efficient LoRA + GRPO on consumer GPUs
- **SkyRL** (UC Berkeley) — scalable RL training
- **torchforge** (Meta PyTorch) — featured GRPO BlackJack example
- **ART** (OpenPipe) — additional integration

Environments are deployed via CLI: `openenv init`, `openenv build` (Docker), `openenv validate`, `openenv push` (to HF Spaces). Our environment descriptor (`openenv.yaml`) specifies a FastAPI runtime on port 8000, conforming to the OpenEnv server protocol.

### The Hackathon

The **OpenEnv Hackathon SF** ran March 7-9, 2026 at Shack15 in San Francisco, organized by Cerebral Valley. Teams of up to 4 built RL environments and post-trained base models to improve performance across select benchmarks. Sponsors and mentors included Meta, Hugging Face, UC Berkeley, Unsloth, Fleet AI, Patronus AI, Scale AI, CoreWeave, OpenPipe, and Cursor.

---

## What We Built: O2 OpenOffice

O2 OpenOffice is a **Gymnasium-compatible multi-agent reinforcement learning environment** where seven LLM-powered agents autonomously run a simulated startup. Our `OfficeOsEnvironment` class implements the full OpenEnv `Environment` interface. Seven agents operate in a shared startup world with role-scoped observations, asymmetric rewards, and a message-passing coordination layer.

Each episode simulates **30 days** of startup operations across **420 turns** (14 turns/day, split into 4 phases: standup, execution, review, planning). Agents take turns round-robin, observing only what their role allows them to see, and producing structured JSON actions that the market simulator executes.

**GitHub**: [github.com/bvsbharat/OpenOfficeRL](https://github.com/bvsbharat/OpenOfficeRL)

---

## Understanding GRPO: The Math Behind Our Training

Before diving into the architecture, let's understand the RL algorithm at the heart of this project. GRPO (Group Relative Policy Optimization) was introduced in the **DeepSeekMath paper** (Shao et al., 2024) and then used as the core training algorithm in **DeepSeek-R1** — where it famously produced the "aha moment" of emergent self-correction in reasoning.

### PPO's Problem: Too Many Models

PPO (Proximal Policy Optimization) requires **four neural networks** in memory simultaneously:

1. **Policy model** — the LLM being trained
2. **Reference model** — frozen copy for KL penalty
3. **Reward model** — evaluates quality of completions
4. **Critic/Value model** — same architecture as policy, estimates state values for computing advantages

For a 14B parameter model, this means ~56B parameters in memory. That's impractical on most hardware.

### GRPO's Insight: Replace the Critic with Group Statistics

GRPO eliminates the critic and reward model entirely. Here's the key idea:

For each prompt $q$, GRPO generates $G$ completions (the "group") from the current policy. Each completion gets a scalar reward. Then:

$$\hat{A}_i = \frac{r_i - \text{mean}(\mathbf{r})}{\text{std}(\mathbf{r})}$$

That's it. The advantage is a simple **Z-score normalization** within the group. No neural network, no GAE (Generalized Advantage Estimation), no value function. This single equation replaces the entire critic model.

### The Full GRPO Loss

The complete objective function:

$$\mathcal{L}_{\text{GRPO}}(\theta) = -\frac{1}{\sum_{i=1}^{G}|o_i|} \sum_{i=1}^{G} \sum_{t=1}^{|o_i|} \left[ \min\left( r_{i,t} \cdot \hat{A}_i, \; \text{clip}(r_{i,t}, \, 1-\epsilon, \, 1+\epsilon) \cdot \hat{A}_i \right) - \beta \cdot D_{\text{KL}}\left[\pi_\theta \| \pi_{\text{ref}}\right] \right]$$

Where:
- $G$ = number of generations per prompt (typically 4-16)
- $r_{i,t} = \frac{\pi_\theta(\text{token}_t)}{\pi_{\text{old}}(\text{token}_t)}$ — the probability ratio (how much the policy has shifted)
- $\hat{A}_i = \frac{r_i - \mu}{\sigma}$ — the group-relative advantage (Z-score)
- $\epsilon$ = clipping parameter (0.2) — the PPO-style trust region
- $\beta$ = KL divergence coefficient (often 0.0 in modern practice)
- The $\min(\cdots)$ is the standard clipped surrogate objective that prevents too-large policy updates

The critical insight: **the advantage is constant across all tokens in a completion**. Unlike PPO where each token gets its own advantage from the critic, GRPO assigns the same per-sequence advantage to every token. If the whole completion was good, every token gets credit. If it was bad, every token gets penalized.

### RLVR: Why Verifiable Rewards Matter

GRPO becomes especially powerful when combined with **RLVR (Reinforcement Learning with Verifiable Rewards)**. Instead of training an expensive neural reward model (which can be gamed), you use programmatic, deterministic reward functions:

- For math: extract the answer, check if it matches ground truth → 1.0 or 0.0
- For code: execute it, run test cases → 1.0 if all pass
- **For our environment**: the market simulation produces deterministic rewards from the action outcome

This is what makes our project a natural fit for GRPO. The `MarketSimulator` is a verifiable reward function — it computes rewards from the state transition, no learned model needed.

### DeepSeek-R1 Results: What GRPO Achieved

DeepSeek-R1 used GRPO to achieve:
- **79.8%** on AIME 2024 (math competition)
- **97.3%** on MATH-500
- **2029** Codeforces rating
- **90.8%** on MMLU

Most remarkably, R1-Zero (pure GRPO, no supervised fine-tuning at all) demonstrated an **emergent "aha moment"** — the model spontaneously developed self-correction behavior during training, learning to re-examine its reasoning when it detected errors. No one programmed this behavior; it emerged purely from the reward signal.

---

## Architecture Deep Dive

### System Architecture

The system has four layers:

**1. Demo API (FastAPI + Uvicorn, port 8080)** — REST + WebSocket bridge:
- `routes.py` → `rl_bridge.py` → `claude_bridge.py` (pluggable LLM routing)
- Endpoints: `/api/reset`, `/api/step`, `/api/state`, `/api/config`, `/api/reconfigure`, `/ws/live`
- Three operating modes: `llm` (Claude for inference), `training` (collect trajectories), `inference` (trained LoRA adapters)
- Hot-swappable model selection at runtime — switch between Claude Haiku/Sonnet/Opus, trained Qwen 2.5 14B LoRA, Qwen3 80B, Llama 3.3 70B, and more via the frontend.

**2. Office OS (Core RL Engine)** — The Gymnasium environment:
- `OfficeOsEnvironment` implements `reset()` → `MarketState.initial(scenario)` and `step(action)` → `MarketSimulator` → `RewardCalculator` → observation
- `BaseAgent` / `LLMAgent` with `MemoryStream` for cognitive state
- `MarketState`, `Simulator`, `EventEngine`, `RewardCalc` for world dynamics
- Scenario engine with 5 adversarial configurations

**3. LLM Providers (Pluggable)** — Anthropic API, AWS Bedrock, vLLM (OpenAI-compatible endpoints). The trained Qwen 2.5 14B with per-role LoRA adapters runs on a Northflank H100.

**4. Frontend (React 19 + Vite)** — Four visualization modes connected via WebSocket:
- **2D Pixel-Art Office (Phaser 3)**: Tiled office layout (40x34 grid, 32px tiles) with animated agent sprites, BFS pathfinding, behavior FSM (IDLE / WORKING / WALKING / COLLABORATING), type-color-coded speech bubbles, and animated collaboration lines between agents.
- **3D Office (React Three Fiber + Drei)**: Roblox-style humanoid agents with orbital camera controls and real-time KPI sidebars.
- **Dashboard**: Real-time KPI charts (traffic, revenue, pipeline value, NPS, team velocity), per-agent reward breakdowns with sparklines, deal pipeline visualization.
- **Playground**: Manual agent action submission for debugging individual agent behavior.

### The Step Function: What Happens Every Turn

The `step()` function in `OfficeOsEnvironment` is where everything converges:

```
1. Snapshot current KPIs (for delta reward calculation)
2. Execute action → MarketSimulator.execute_action()
   - Validates action is allowed for the agent's role
   - Updates MarketState (pipeline, features, content, campaigns)
   - Handles multi-turn actions (BUILD_FEATURE takes 3 turns)
3. Fire events → EventEngine.tick()
   - Check scheduled scenario events (fixed-day triggers)
   - Roll for random events (8 types, ~15% chance/day)
4. Advance simulation clock
5. Calculate reward → RewardCalculator.calculate()
   - 6-component composite (detailed below)
6. Sync to Google Sheets (if integration enabled)
7. Build role-scoped observation for the next agent
8. Return (observation, reward, terminated, truncated, info)
```

### Observation Space: Asymmetric Information

This is a critical design choice borrowed from multi-agent RL theory. In cooperative MARL, a common approach is **Centralized Training, Decentralized Execution (CTDE)** — agents only see local observations but can share information. We take this further: agents don't share a god-view of the world. Each role sees only what it needs, forcing information sharing through messages.

**Role-scoped KPI visibility:**
- **CEO/Marketing**: See all KPIs — traffic, revenue, conversion, brand awareness, pipeline value, budget, NPS
- **Dev**: Sees product stability, feature count, bug count, team velocity — but not revenue or pipeline details
- **Sales**: Sees revenue, MRR, pipeline with full customer details (names, stages, objections, contract tiers) — but not technical metrics
- **Content/HR/Customer**: Filtered views matching their domain

**Shared across all agents:**
- `team_status`: A summary dict showing what every other team is doing
- `shared_memory`: Last 15 entries from the shared memory board
- `recent_events`: Any events that fired this turn

This asymmetric information design creates a natural need for coordination. Sales doesn't know if Dev has bugs to fix; Dev doesn't know if a big deal is about to close. The only way to align is through messages — and agents learn to send them because the collaboration bonus rewards it.

### Agent Decision Flow (Per Turn)

```
Environment State
    → Build Observation (role-scoped KPIs, pipeline, messages, events, memory)
    → Token-Aware Pruning (priority P0–P8, fits context window)
    → LLM Agent Decides → AgentAction { action_type, target, parameters, reasoning, message }
    → Validate (role-allowed actions only; reject + retry up to 8x)
    → Execute: MarketSimulator + EventEngine + Collaboration Detection
    → RewardCalculator: R = pipeline_stage + kpi_delta + action_reward
                            + collaboration_bonus - penalties + base_shaping
    → Update Memory Stream → Reflect → Plan → Broadcast
```

---

## The Seven Agents

Each agent has a distinct role, a scoped set of allowed actions, and asymmetric reward drivers:

| Agent | Key Actions | Primary Reward Drivers |
|-------|------------|----------------------|
| **CEO** (Jeeya) | `SET_OKRS`, `ALLOCATE_BUDGET`, `REVIEW_STRATEGY`, `PIVOT`, `SEND_DIRECTIVE`, `APPROVE_INITIATIVE` | Closed deals (+5.0), churned customers (-3.0), budget efficiency |
| **Dev** (Alex) | `BUILD_FEATURE`, `FIX_BUG`, `SHIP_RELEASE`, `REFACTOR`, `WRITE_DOCS`, `REVIEW_PR` | Feature ships (+3.0), demos (+1.0), churn (-5.0), stability |
| **Marketing** (Jordan) | `LAUNCH_CAMPAIGN`, `RUN_AD`, `RESEARCH_MARKET`, `ANALYZE_COMPETITOR`, `OPTIMIZE_FUNNEL`, `A_B_TEST` | Leads (+1.5), closed deals (+3.0), traffic, conversion rate |
| **Sales** (Sam) | `QUALIFY_LEAD`, `RUN_DEMO`, `SEND_PROPOSAL`, `CLOSE_DEAL`, `FOLLOW_UP`, `COLLECT_FEEDBACK` | Closed deals (+10.0), pipeline progression, lost deals (-3.0) |
| **Content** (Casey) | `WRITE_BLOG`, `WRITE_SOCIAL_POST`, `WRITE_CASE_STUDY`, `WRITE_EMAIL_SEQUENCE`, `WRITE_DOCS`, `REVISE_CONTENT` | Visitor traffic (+0.5), leads (+1.0), closed deals (+2.0) |
| **HR** (Pat) | `PLAN_SPRINT`, `TRACK_OKRS`, `RESOLVE_BLOCKER`, `HIRE_CONTRACTOR`, `PERFORMANCE_REVIEW`, `TEAM_SYNC` | Team velocity, blocker resolution (+1.5), OKR tracking |
| **Customer** (Oracle) | `EVALUATE_PRODUCT`, `REQUEST_FEATURE`, `GIVE_FEEDBACK`, `REFER_LEAD`, `ESCALATE_ISSUE`, `RENEW_CONTRACT` | NPS, satisfaction, expansion revenue, churn signals (-5.0) |

### Cognitive Architecture: Smallville-Style Memory

Each agent implements a memory system inspired by Stanford's **"Generative Agents: Interactive Simulacra of Human Behavior"** (Park et al., 2023). In that paper, 25 agents inhabit a sandbox world called Smallville — waking up, working, socializing — all behavior emergent from three cognitive components:

**1. Memory Stream**: A growing record of experiences, each with an importance score (1-10, rated by the LLM). Our `MemoryStream` has a 200-entry capacity with LRU eviction.

**2. Retrieval Function**: When an agent needs to act, memories are scored by combining:

$$\text{score} = \text{recency} \times \text{importance} \times \text{relevance}$$

Where recency uses exponential decay: $\text{score} = \text{importance} \times e^{-0.01 \times \text{age}}$. Top-scoring memories are injected into the prompt as context.

**3. Reflection**: Periodically (every 70 turns), agents synthesize higher-level insights from recent memories. A Sales agent might reflect: "Fintech deals close faster when we demo the analytics dashboard first." These reflections are stored back as first-class memories with high importance scores, creating a hierarchy: raw observations at the leaves, reflections in the middle, meta-reflections at the root.

**4. Plans**: High-level strategies updated based on reflections, guiding the agent's action selection.

### Token-Aware Prompt Construction

Prompts are built per-turn with **priority-based token pruning** using 8 tiers (P0 = critical KPIs/pipeline, P8 = call to action). When the total prompt exceeds the model's context window, lower-priority sections are dropped first. This makes the environment model-agnostic — run it with Claude Opus (200K context) or Gemma 3 4B (8K context) and the pruning adapts automatically.

### Action Validation and Structured Output

Every agent response must be valid JSON:

```json
{
  "action_type": "QUALIFY_LEAD",
  "target": "Acme Corp",
  "parameters": { "approach": "technical_demo" },
  "reasoning": "Acme has been in visitor stage for 3 days with high intent...",
  "message": "marketing: can you send the case study on fintech integrations?"
}
```

If the LLM produces invalid output (malformed JSON, wrong action for role, missing fields), the system retries up to 8 times with increasingly explicit error feedback.

---

## The Market Simulation Engine

The `MarketSimulator` is where the environment's complexity lives. It implements **42+ action handlers** across all 7 roles, each with domain-specific mechanics.

### Multi-Turn Actions

Not everything happens instantly. Several actions span multiple turns, creating planning horizons:

- **`BUILD_FEATURE`**: Takes **3 turns** to complete. The feature enters a `turns_remaining` countdown. `SHIP_RELEASE` only succeeds when `turns_remaining == 0`. Starting a feature on day 28 means it won't ship before the episode ends.
- **Content creation**: Multi-turn process with draft → revision stages.
- **Sales pipeline**: Customers must move through stages in order: `visitor → lead → qualified → demo → proposal → negotiation → closed_won`. You can't skip stages — `CLOSE_DEAL` on a lead that hasn't been through demo fails.

### Probabilistic Deal Closing

`CLOSE_DEAL` is the most complex action. Success probability depends on multiple factors:

```
base_probability = 0.4

Modifiers:
  + shipped_features × 0.1      (product readiness)
  + content_touchpoints × 0.05  (marketing collateral)
  + satisfaction × 0.2           (customer happiness)
  - unresolved_objections × 0.15 (blockers)
  + product_stability × 0.1      (reliability)
  - company_size_factor           (enterprise = harder)
```

Contract tier creates a genuine risk/reward tradeoff: monthly contracts close easier but pay less. Annual contracts are harder but trigger the **3x reward multiplier** on `closed_won`.

### Customer Lifecycle

The `MarketState` manages a full customer pipeline:
- **Lead spawning**: New visitors appear based on traffic (influenced by Marketing campaigns and Content)
- **Lead decay**: Leads not contacted within 5 days generate stale lead penalties (-0.5 each)
- **MRR accrual**: Closed deals generate recurring monthly revenue
- **Churn risk**: Low NPS, low satisfaction, or unresolved bugs trigger churn
- **Referrals**: Happy customers (`REFER_LEAD`) generate new leads with a 5-day cooldown

### The Event Engine

The simulation isn't static. Two mechanisms inject chaos:

**Random Events** (~15%/day): Competitor Launch, Viral Moment, PR Crisis, Algorithm Change, Budget Cut, Big Customer Inquiry, Feature Request Wave, Customer Success Story.

**Scheduled Scenario Events**: Fixed-day triggers per scenario. For example, the **Competitor Launch** scenario fires: Day 3 (funding news), Day 7 (feature parity), Day 15 (poaching attempt), Day 25 (PR crisis). These create reproducible stress tests for comparing pre-training vs post-training behavior.

---

## Reward Function: The Core Design

The reward signal is a **composite function** with six components, calculated per-agent per-turn:

```
R(agent, turn) = pipeline_stage_reward      # Customer moves through funnel
               + kpi_delta_reward            # Improvement in role-specific KPIs
               + action_reward               # Direct outcome of the action taken
               + collaboration_bonus         # Building on another agent's work
               - constraint_penalties        # Budget overruns, invalid targets
               + base_shaping               # +0.1 for any successful action (ensures gradient)
```

### Asymmetric Pipeline Stage Rewards

This is where the organizational tension lives. The same event produces different reward magnitudes for each role:

| Stage | Sales | Marketing | Dev | Content | CEO | HR | Customer |
|-------|-------|-----------|-----|---------|-----|----|---------|
| lead | — | +1.5 | — | +1.0 | — | — | — |
| demo | +1.5 | — | +1.0 | — | — | — | — |
| proposal | +2.0 | — | — | — | — | — | — |
| **closed_won** | **+10.0** | +3.0 | +2.0 | +2.0 | +5.0 | +1.0 | +2.0 |
| closed_lost | -3.0 | -1.0 | — | -0.5 | -2.0 | -0.5 | — |
| **churned** | -3.0 | -1.0 | **-5.0** | -2.0 | -3.0 | -1.0 | **-5.0** |

**Contract tier multipliers** on `closed_won`: monthly (1.0x), 6-month (2.0x), annual (3.0x).

Sales gets +10 for a deal but Dev gets -5 for churn. This is a deliberate design from multi-agent RL theory: **asymmetric rewards create natural tensions that mirror actual organizations**. In MARL literature, this creates a "mixed-motive" environment — agents must balance self-interest with cooperation, because no single agent can maximize their own reward without the others performing well.

### Collaboration Detection

Detected through two mechanisms:
- **Message-based**: Agent mentions another agent by name (e.g., Marketing says `"dev: align launch with feature ship"`)
- **Target-based**: Agent's `target` references another agent's domain

Specific bonuses: Content writing about a shipped feature (+1.0), Sales referencing content in demos (+0.5), Dev building from customer feedback (+1.0), Marketing promoting content (+0.5). **Churn prevention bonus**: extra rewards when satisfaction < 0.4 for crisis-appropriate actions.

### Constraint Penalties

- Budget overrun: -0.5
- Invalid action: -1.0
- Stale leads (>5 days without contact): **-0.5 per lead**
- Vaporware (content referencing unshipped features): **-5.0**
- Sales not updating pipeline by end of day: -1.0

### Base Shaping: Why +0.1 Matters for GRPO

Every successful action gets +0.1. This seems trivial but is critical for GRPO training. GRPO works by comparing multiple completions within a group via Z-score normalization. If most turns produce 0.0 reward, $\sigma(\mathbf{r}) \approx 0$ and the normalization produces near-zero advantages — no learning signal. The +0.1 base ensures that even "maintenance" turns (team syncs, planning, docs) produce non-zero rewards, giving GRPO gradient signal on every single turn of a 420-turn episode.

---

## Training Pipeline: GRPO + LoRA on Qwen 2.5 14B

### Understanding LoRA: How We Fine-Tune a 14B Model

**LoRA (Low-Rank Adaptation)** makes fine-tuning a 14B parameter model feasible on a single GPU. The core idea from Hu et al. (2021):

For any pretrained weight matrix $W_0$ (shape $d \times k$), LoRA constrains the update to be low-rank:

$$W = W_0 + \Delta W = W_0 + BA$$

Where $B \in \mathbb{R}^{d \times r}$ and $A \in \mathbb{R}^{r \times k}$ are small matrices, and $r \ll \min(d, k)$ is the rank. The forward pass becomes:

$$h = W_0 x + \frac{\alpha}{r} \cdot BAx$$

Key properties:
- $B$ is initialized to zero, so training starts from the exact pretrained model
- At rank 32 on a 14B model, trainable parameters are ~0.3-0.6% of total — we're training millions of parameters, not billions
- At inference, LoRA weights can be **merged** back into the base model with zero overhead: $W_{\text{merged}} = W_0 + \frac{\alpha}{r} \cdot BA$
- Multiple LoRA adapters can be **hot-swapped** on the same base model

We target **all attention and MLP projections**: `q_proj`, `k_proj`, `v_proj`, `o_proj`, `gate_proj`, `up_proj`, `down_proj`. This covers the full information flow through each transformer layer.

### Why Unsloth?

**Unsloth** makes GRPO + LoRA practical by dramatically reducing VRAM requirements:

| Aspect | Standard | With Unsloth | Savings |
|--------|----------|--------------|---------|
| GRPO VRAM | Baseline | **80% less** | 80% |
| Training speed | 1x | **1.5-2x faster** | 50-100% |
| Context length | Limited | **7x longer** (custom gradient checkpointing) | 7x |

Unsloth integrates directly with TRL's `GRPOTrainer` by patching it at import time. Key optimizations include:
- **Dynamic 4-bit Quantization**: Selectively avoids quantizing certain parameters, improving accuracy with <10% more VRAM than standard BnB 4-bit
- **Custom gradient checkpointing**: Recomputes activations during backward pass instead of storing them, enabling 7x longer context windows — essential for GRPO since generating multiple completions multiplies effective sequence length
- **vLLM-backed fast inference**: When `fast_inference=True`, generation during GRPO (the bottleneck) is accelerated by vLLM's PagedAttention

### The Training Worker: What Runs on the H100

The training worker (`train_worker.py`) is an HTTP server on port 8081 running on a Northflank H100. It exposes three endpoints:

- `GET /health` — Status check
- `POST /train` — Train a role with GRPO
- `POST /hotload` — Hot-load a trained LoRA into vLLM

Here's what happens when `/train` is called:

**Model Loading** (via Unsloth):
```python
model, tokenizer = FastLanguageModel.from_pretrained(
    "Qwen/Qwen2.5-14B-Instruct",
    load_in_4bit=True,          # 4-bit quantization
    max_seq_length=4096,
)

model = FastLanguageModel.get_peft_model(
    model,
    r=32,                        # LoRA rank
    lora_alpha=32,               # Scaling factor (alpha/r = 1.0)
    target_modules=[             # All attention + MLP projections
        "q_proj", "k_proj", "v_proj", "o_proj",
        "gate_proj", "up_proj", "down_proj"
    ],
    use_gradient_checkpointing="unsloth",  # 7x longer context
)
```

**GRPO Configuration:**
```python
GRPOConfig(
    num_generations=4,              # 4 completions per prompt (reduced for 14B VRAM)
    max_prompt_length=3072,         # Context budget for prompts
    max_completion_length=1024,     # Max tokens per completion
    temperature=0.9,                # High temp = diverse rollouts
    learning_rate=2e-5,
    per_device_train_batch_size=1,
    gradient_accumulation_steps=4,  # Effective batch = 4
    num_train_epochs=3,
    max_steps=min(50, len(rows)*3), # Cap per episode
    bf16=True,
    optim="adamw_8bit",             # 8-bit Adam for memory efficiency
)
```

**Why `temperature=0.9`?** GRPO requires **diverse rollouts** to produce meaningful advantages. If all 4 completions are identical (low temperature), $\sigma(\mathbf{r}) \approx 0$ and the Z-score normalization produces zero advantage — no learning. High temperature ensures each completion takes a different strategic approach, giving GRPO the variance it needs.

**Why `num_generations=4` not 8?** The default in TRL is 8, but we reduced to 4 to fit Qwen 2.5 14B on a single H100 with room for the optimizer states. This is the main VRAM knob — reduce it first if you hit OOM.

### Dual Reward Functions for GRPO

The `GRPOTrainer` receives **two reward functions** that score each generated completion. This is where our environment's reward signal connects to the GRPO algorithm:

**1. Rule-Based Scorer (`score_completion`)** — Deterministic, 0–1.45 range:

```
+0.30  Valid JSON output
+0.10  Clean JSON only (no extra text)
+0.20  Contains action_type field
+0.30  Action is valid for this role (-0.20 penalty if wrong)
+0.20  Reasoning has 10+ words (+0.10 for 5+)
+0.10  Non-empty target field
+0.10  Target references context entities (customer names, features)
+0.10  Message follows "role: text" format
+0.05  Non-empty parameters dict
```

This enforces **structural correctness** — the model learns to produce well-formed agent actions. The role-action validation is key: it penalizes a Dev agent that tries to `CLOSE_DEAL` or a Sales agent that tries to `BUILD_FEATURE`.

**2. LLM-as-a-Judge (`llm_judge_reward`)** — Strategic quality, 0.0–1.0 range:

A judge model (configurable: Bedrock Claude, Anthropic API, OpenRouter, or local vLLM) rates each completion 1-5 on strategic quality given the context. Normalized to 0.0-1.0. Falls back to 0.25 on error.

This mirrors DeepSeek-R1's approach in its "Diverse RL Phase" where they combined rule-based rewards for deterministic tasks with LLM-as-judge for subjective quality. The combination ensures agents learn both **format compliance** and **strategic reasoning**.

### The Full Training Loop

```
Simulation Episodes → Trajectory Collector → Northflank H100 → vLLM Hot-Load
```

**Step 1: Collect.** During simulation, `TrajectoryCollector` records every agent turn as a `TurnRecord`:

```json
{
  "role": "sales",
  "system_prompt": "You are the Sales agent...",
  "user_message": "=== Day 3 | Phase: execution...",
  "assistant_response": {
    "action_type": "QUALIFY_LEAD",
    "target": "Acme Corp",
    "reasoning": "..."
  },
  "reward": 2.1,
  "day": 3,
  "turn": 25
}
```

**Step 2: Ship.** After each episode, trajectories are grouped by role, saved as JSONL, and sent to the H100 via HTTP POST.

**Step 3: Train.** The worker runs GRPO for each of the 6 trained roles (Customer is explicitly skipped — it's the reward oracle, using the base model). Each role gets its own LoRA adapter: `office-os-ceo`, `office-os-dev`, `office-os-marketing`, `office-os-sales`, `office-os-content`, `office-os-hr`.

After training each role, GPU memory is explicitly freed (`del model`, `gc.collect()`, `torch.cuda.empty_cache()`) before training the next — critical for fitting 6 sequential training runs on a single H100.

**Step 4: Deploy.** Trained LoRA adapters are hot-loaded into the running vLLM server:

```bash
vllm serve Qwen/Qwen2.5-14B-Instruct \
  --enable-lora \
  --max-loras 2 \
  --max-lora-rank 32 \
  --gpu-memory-utilization 0.6 \
  --max-model-len 4096
```

vLLM can serve multiple LoRA adapters on a single base model simultaneously. Each adapter adds approximately `2 × num_layers × rank × hidden_dim × dtype_size` bytes — for rank 32, that's only ~8MB per adapter. Hot-loading via POST to `/v1/load_lora_adapter` means no server restart needed. Subsequent episodes use the fine-tuned models immediately.

**Step 5: Iterate.** The loop repeats across 10 episodes cycling through all 5 scenarios, progressively improving agent behavior.

### Expert Data Bootstrapping

Cold-starting GRPO on random model outputs is painful — initial trajectories are garbage. To solve this, `generate_training_data.py` implements a **rule-based expert policy**:

- Hand-crafted optimal action sequences per role with KPI-aware reasoning
- Context-specific messages referencing real customer names and features
- **Negative examples included** — mediocre actions with low rewards. GRPO needs reward variance within each group; if all examples are perfect, $\sigma(\mathbf{r}) \approx 0$ and no learning happens
- 50+ episodes across all 5 scenarios
- Outputs per-role JSONL files ready for `GRPOTrainer`

This is analogous to DeepSeek-R1's "Cold Start Phase" — a short SFT priming before GRPO to establish a reasonable behavioral baseline.

Pre-generated trajectories: `office_os/training_data/`. Trained weights: [HarshalH/office-os-loras](https://huggingface.co/HarshalH/office-os-loras).

---

## Five Adversarial Scenarios

Each scenario modifies initial state, injects customers/backlog, and fires scheduled events:

| Scenario | Budget | Traffic | Pressure | Key Events |
|----------|--------|---------|----------|------------|
| **Baseline GTM Launch** | $100K | 1,000/day | Low | None — standard playbook |
| **Competitor Launch** | $100K | 800/day (-20%) | High | Day 3: funding news, Day 7: feature parity, Day 15: poaching, Day 25: PR crisis. 1.5x event probability |
| **Series A Pressure** | $200K (2x) | 1,000/day | High | Day 1: board meeting, Day 30: check-in, Day 60: final stretch. Must 3x MRR |
| **Churn Spike** | $100K | 1,000/day | Critical | Day 1: warning, Day 5: escalation, Day 10: churn begins, Day 20: recovery. Starts NPS 25, satisfaction 0.3, 4 critical bugs |
| **Viral Moment** | $100K | 3,000/day (3x) | Chaotic | Day 1: viral tweet, Day 3: lead flood, Day 7: infra strain, Day 15: support overload. 6 leads, 4 extra customers |

These create reproducible stress tests. In "Churn Spike," the environment starts in crisis: NPS 25, satisfaction 0.3, stability 0.5, 4 critical bugs. Dev and Customer agents are under immediate pressure while Sales has nothing to work with. In "Viral Moment," 3x traffic sounds great until infrastructure buckles and support requests overwhelm the team.

---

## Emergent Behaviors

The most compelling results emerged purely from the reward structure — no explicit coordination rules:

**Emergent Collaboration**: Marketing started timing campaign launches to coincide with Dev's feature releases. Sales began checking with Dev before promising delivery timelines. In MARL theory, this is "emergent communication" — agents develop ad-hoc signaling protocols from reward pressure alone.

**Natural Role Specialization**: Over training, agents developed distinct action distributions. CEO focused on resource allocation, Sales became aggressive early and conservative late. This mirrors findings from OpenAI's multi-agent Hide-and-Seek experiments where agents spontaneously specialized without role assignment.

**Organizational Memory**: Through the Smallville-style memory stream, agents developed institutional knowledge. Reflections like "enterprise deals need 3+ content touchpoints before proposal" carried across turns, creating long-horizon planning.

**Vaporware Avoidance**: The -5.0 penalty forced Content to coordinate with Dev before publishing. Content agents learned to message Dev asking "what's shipping this week?" — a behavior no one programmed.

**Churn Prevention Mode**: When satisfaction dropped below 0.4, agents collectively shifted from growth to retention. Dev prioritized bug fixes over features, Sales paused outreach, Content pivoted to support docs. This emerged from the collaboration bonus system rewarding crisis-appropriate actions.

---

## Running It Yourself

### Quick Start

```bash
# Clone
git clone https://github.com/bvsbharat/OpenOfficeRL.git
cd OpenOfficeRL

# Backend
pip install -e office_os/

# Frontend
cd demo/frontend && npm install && cd ../..

# Run (pick a model backend)
cd demo
npm run BE_LLM        # Claude on Bedrock (default)
npm run BE_TRAINED     # Trained Qwen 2.5 14B LoRA on Northflank vLLM
npm run BE_ART         # Custom vLLM endpoint

# Frontend (separate terminal)
npm run start
# Open http://localhost:5173
```

### Headless Mode

```bash
# Single episode
python office_os/run_agents.py --scenario baseline --use-claude --days 30

# Full training loop (10 episodes x 5 scenarios)
python office_os/train_loop.py --northflank-endpoint https://your-endpoint --episodes 10

# Generate expert training data (no LLM needed)
python office_os/generate_training_data.py

# Dry run (collect trajectories, skip training)
python office_os/train_loop.py --use-claude --dry-run
```

### Tests

12 unit tests covering reset, multi-turn features, campaigns, vaporware penalty, pipeline progression, messaging, rewards, contract tiers, and episode termination:

```bash
python -m pytest office_os/tests/test_env.py -v
```

---

## Key Takeaways

1. **GRPO gives you deep intuition for fine-tuning.** The Z-score normalization $\hat{A}_i = (r_i - \mu) / \sigma$ within a group of completions — that single equation replaces the entire critic model from PPO. Understanding this makes the whole RL-for-LLMs landscape click.

2. **Environments are the product.** The RL community talks about algorithms, but the bottleneck is environments. OpenEnv's mission to standardize environment creation with Gymnasium-style APIs is exactly right. The environment *is* the curriculum.

3. **Multi-agent systems surface real organizational dynamics.** Asymmetric rewards create mixed-motive environments where agents must balance self-interest with cooperation — just like actual companies. The -5.0 vaporware penalty alone produced emergent coordination without any explicit rule.

4. **The training loop matters as much as the architecture.** Collect → Ship → Train → Deploy → Iterate. Per-role LoRA adapters trained on role-specific rewards, hot-loaded into vLLM for the next episode — this closed loop is what makes agents actually improve.

5. **Dual reward functions cover different learning objectives.** Rule-based scoring teaches format compliance; LLM-as-judge teaches strategic quality. Neither alone produces agents that both follow the schema and make smart decisions.

6. **Base shaping prevents reward sparsity.** +0.1 for any successful action is the difference between GRPO having gradient signal and having none. In a 420-turn episode, most turns are maintenance — without it, the model only learns from the handful of turns that move the pipeline.

7. **LoRA + Unsloth + 4-bit quantization makes the impossible feasible.** Training 6 separate LoRA adapters on a 14B model on a single H100, sequentially, with GRPO generating 4 completions per prompt — this would be impossible without aggressive memory optimization.

---

## Links

- **Try it**: [O2 OpenOffice App](https://lnkd.in/g8ux99ZX)
- **Demo Video**: [Watch the Demo](https://lnkd.in/grrxNRWW)
- **GitHub**: [github.com/bvsbharat/OpenOfficeRL](https://github.com/bvsbharat/OpenOfficeRL)
- **Model Weights**: [HarshalH/office-os-loras](https://huggingface.co/HarshalH/office-os-loras)

---

## Acknowledgments

Huge thanks to my teammates **Jeeya Khetia** and **Harshal J Hirpara** from the rest of the team. Shoutout to **Sanyam Bhutani**, **Daniel Han**, and the teams at **PyTorch**, **Meta**, **Cerebral Valley**, **Hugging Face**, **Patronus AI**, **Scale AI**, **Northflank**, **OpenPipe**, and **Unsloth AI** for the infrastructure and support.

---

*Multi-agent. Multi-mind. One office.*
