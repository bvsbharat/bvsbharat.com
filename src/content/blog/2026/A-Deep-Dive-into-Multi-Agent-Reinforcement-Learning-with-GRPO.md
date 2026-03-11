# From Fine-Tuning Curiosity to Training a Virtual Startup: A Deep Dive into Multi-Agent Reinforcement Learning with GRPO

*How exploring LLM fine-tuning led to building a Gymnasium-compatible RL environment where 7 LLM-powered agents run a company — trained with GRPO + LoRA on Qwen 2.5 14B — and what we learned about reward design, emergent collaboration, and the future of agentic AI.*

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

## What We Built: O2 OpenOffice

O2 OpenOffice is a **Gymnasium-compatible multi-agent reinforcement learning environment** where seven LLM-powered agents autonomously run a simulated startup. Built on Meta's **OpenEnv framework** — an e2e framework for creating, deploying and using isolated execution environments for agentic RL training using Gymnasium-style APIs (`step()`, `reset()`, `state()`).

OpenEnv was designed by Meta-PyTorch and Hugging Face to standardize the agentic RL community. It provides tools for environment creators to build environments that are isolated, secure, and easy to deploy — while ensuring interoperability with popular RL tools like TRL, Unsloth, SkyRL, and veRL.

Our environment (`OfficeOsEnvironment`) implements the full OpenEnv/Gymnasium interface. Seven agents operate in a shared startup environment with role-scoped observations, asymmetric rewards, and a message-passing coordination layer.

**GitHub**: [github.com/bvsbharat/OpenOfficeRL](https://github.com/bvsbharat/OpenOfficeRL)

---

## Architecture Deep Dive

### System Architecture

The system has four layers:

**1. Frontend (React 19 + Vite)** — Four visualization modes connected via WebSocket:
- **2D Pixel-Art Office (Phaser 3)**: Tiled office layout (40x34 grid, 32px tiles) with animated agent sprites, BFS pathfinding, behavior FSM (IDLE / WORKING / WALKING / COLLABORATING), type-color-coded speech bubbles, and animated collaboration lines between agents. Camera supports pan/zoom with sprite caching across 6 zoom levels.
- **3D Office (React Three Fiber + Drei)**: Roblox-style humanoid agents with orbital camera controls and real-time KPI sidebars.
- **Dashboard**: Real-time KPI charts (traffic, revenue, pipeline value, NPS, team velocity), per-agent reward breakdowns with sparklines, deal pipeline visualization.
- **Playground**: Manual agent action submission for debugging individual agent behavior.

**2. Demo API (FastAPI + Uvicorn, port 8080)** — REST + WebSocket bridge:
- `routes.py` → `rl_bridge.py` → `claude_bridge.py` (pluggable LLM routing)
- Endpoints: `/api/reset`, `/api/step`, `/api/state`, `/api/config`, `/api/reconfigure`, `/ws/live`
- Hot-swappable model selection at runtime — switch between Claude Haiku/Sonnet/Opus, trained Qwen 2.5 14B LoRA, Qwen3 80B, Llama 3.3 70B, and more via the frontend model selector.

**3. Office OS (Core RL Engine)** — The Gymnasium environment:
- `OfficeOsEnvironment` implements `reset()` → `MarketState.initial(scenario)` and `step(action)` → `MarketSimulator` → `RewardCalculator` → observation
- `BaseAgent` / `LLMAgent` with `MemoryStream` for cognitive state
- `MarketState`, `Simulator`, `EventEngine`, `RewardCalc` for world dynamics
- Scenario engine with 5 adversarial configurations

**4. LLM Providers (Pluggable)** — Anthropic API, AWS Bedrock, vLLM (OpenAI-compatible endpoints). The trained Qwen 2.5 14B with per-role LoRA adapters runs on a Northflank H100.

### Agent Decision Flow (Per Turn)

Each turn follows this pipeline:

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

### Cognitive Architecture (Smallville-Style)

Each agent implements a memory system inspired by Stanford's "Generative Agents" paper (Park et al., 2023):

- **Observations**: Raw environment events stored with importance scores
- **Reflections**: Periodically synthesized insights from recent memories (e.g., a Sales agent reflecting "fintech deals close faster" after three wins)
- **Plans**: High-level strategies updated based on reflections
- **Retrieval**: Recency + importance scoring with exponential decay (capacity: 200 memories, LRU eviction)

Prompts are built per-turn with **priority-based token pruning** (P0 = KPIs/pipeline, P8 = call to action). Lower-priority sections are dropped to fit any model's context window — making the environment model-agnostic.

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

Sales gets +10 for a deal but Dev gets -5 for churn. This forces agents to negotiate through their actions: Sales can't over-promise without Dev bearing the penalty.

### Collaboration Detection

Detected through two mechanisms:
- **Message-based**: Agent mentions another agent by name (e.g., Marketing says `"dev: align launch with feature ship"`)
- **Target-based**: Agent's `target` references another agent's domain (e.g., Sales targets a feature Dev just shipped)

### Constraint Penalties

- Budget overrun: -1.0
- Invalid action: -1.0
- Stale leads (not contacted >5 days): -0.5 per lead
- Vaporware (content referencing unshipped features): **-5.0**

---

## Training Pipeline: GRPO + LoRA on Qwen 2.5 14B

### Why GRPO?

GRPO (Group Relative Policy Optimization), developed by DeepSeek for their R1 reasoning models, differs from PPO in two critical ways:

1. **The value model is removed** — replaced with statistics from sampling the LLM multiple times. For a given prompt, GRPO generates multiple completions (rollouts), computes rewards for each, calculates the mean and standard deviation, then Z-score normalizes to produce advantages. This is the "group relative" part — baselines come from the group itself.

2. **The reward model is removed** — replaced with verifiable reward functions (RLVR). Our composite reward function produces deterministic rewards from the market simulation, no learned reward model needed.

This means GRPO needs only the policy and reference models in memory (vs. four models for PPO), making it feasible to train on a single H100.

### Our Training Loop

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

**Step 2: Ship.** After each episode, trajectories are saved as JSONL and sent to the Northflank H100 training worker via HTTP.

**Step 3: Train.** The worker runs GRPO using **TRL** (Hugging Face's Transformer Reinforcement Learning library) + **Unsloth** for efficient LoRA fine-tuning. The base model is **Qwen 2.5 14B Instruct**. Each of the 7 roles gets its own LoRA adapter trained on role-specific reward signals:
- `office-os-ceo`
- `office-os-dev`
- `office-os-marketing`
- `office-os-sales`
- `office-os-content`
- `office-os-hr`

Unsloth enables this to work with dramatically less VRAM — making LoRA+GRPO feasible where full fine-tuning would be impossible. On 20K context lengths with 8 generations per prompt, Unsloth uses approximately 90% less VRAM compared to standard implementations with Flash Attention 2.

**Step 4: Deploy.** Trained LoRA adapters are hot-loaded into vLLM. Subsequent episodes use the fine-tuned models for inference. Model switching is supported at runtime via the `/api/reconfigure` endpoint.

**Step 5: Iterate.** The loop repeats across episodes and scenarios, progressively improving agent behavior.

Pre-generated expert trajectories are available in `office_os/training_data/` for bootstrapping, and trained model weights are published on Hugging Face: [HarshalH/office-os-loras](https://huggingface.co/HarshalH/office-os-loras).

---

## Five Adversarial Scenarios

Each scenario modifies initial state, injects customers/backlog, and fires scheduled events. Random events also fire with configurable probability (default 15%/day):

| Scenario | Budget | Traffic | Pressure | Key Events |
|----------|--------|---------|----------|------------|
| **Baseline GTM Launch** | $100K | 1,000/day | Low | None — standard playbook |
| **Competitor Launch** | $100K | 800/day | High | Day 3: funding news, Day 7: feature parity, Day 15: poaching attempt, Day 25: PR crisis |
| **Series A Pressure** | $200K | 1,000/day | High | Day 1: board meeting, Day 30: check-in, Day 60: final stretch. Must 3x MRR in 90 days |
| **Churn Spike** | $100K | 1,000/day | Critical | Day 1: warning signs, Day 5: escalation, Day 10: churn begins, Day 20: recovery check |
| **Viral Moment** | $100K | 3,000/day | Chaotic | Day 1: viral tweet, Day 3: lead flood, Day 7: infra strain, Day 15: support overload |

These scenarios stress-test the environment by shifting reward dynamics mid-episode. In "Competitor Launch," agents must pivot strategies when facing feature parity. In "Viral Moment," the Sales and HR agents face cascading load while Dev deals with infrastructure strain.

---

## Emergent Behaviors

The most compelling results emerged purely from the reward structure:

**Emergent Collaboration**: Without any explicit coordination protocol, agents learned to reference each other's work. Marketing started timing campaign launches to coincide with Dev's feature releases. Sales began checking with Dev before promising delivery timelines to customers.

**Natural Role Specialization**: Over training, agents developed distinct action distributions. The CEO focused on resource allocation rather than task execution. Sales became more aggressive early in episodes and conservative near closing.

**Organizational Memory**: Through the memory stream (200-memory capacity with LRU eviction), agents developed institutional knowledge. Strategies that worked in past episodes influenced future behavior.

**Vaporware Avoidance**: The -5.0 penalty for content referencing unshipped features forced Content and Marketing to coordinate with Dev before publishing — a behavior that emerged without any coordination rule.

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

# Full training loop (10 episodes × 5 scenarios)
python office_os/train_loop.py --northflank-endpoint https://your-endpoint --episodes 10
```

---

## Key Takeaways

1. **RL gives you deep intuition for fine-tuning.** Understanding how GRPO eliminates the critic model through group statistics, how advantages are computed via Z-score normalization across rollouts, and how verifiable rewards replace learned reward models — this gives you a mental model for why RL-based fine-tuning works.

2. **Environments are the product.** The RL community talks about algorithms, but the bottleneck is environments. OpenEnv's mission to standardize environment creation with Gymnasium-style APIs is exactly right. The environment *is* the curriculum.

3. **Multi-agent systems surface real organizational dynamics.** Asymmetric rewards create natural tensions that mirror actual companies. The -5.0 vaporware penalty alone produced emergent coordination between Content and Dev without any explicit rule.

4. **The training loop matters as much as the architecture.** Collect → Ship → Train → Deploy → Iterate. Each of the 7 roles getting its own LoRA adapter, trained on role-specific rewards, then hot-loaded into vLLM for the next episode — this closed-loop approach is what makes the agents actually improve.

---

## Links

- 🖥️ **Try it**: [O2 OpenOffice App](https://lnkd.in/g8ux99ZX)
- 📺 **Demo Video**: [Watch the Demo](https://lnkd.in/grrxNRWW)
- 💻 **GitHub**: [github.com/bvsbharat/OpenOfficeRL](https://github.com/bvsbharat/OpenOfficeRL)
- 🤗 **Model Weights**: [HarshalH/office-os-loras](https://huggingface.co/HarshalH/office-os-loras)

---

## Acknowledgments

Huge thanks to my teammates **Jeeya Khetia** and the rest of the team. Shoutout to **Sanyam Bhutani**, **Daniel Han**, and the teams at **PyTorch**, **Meta**, **Cerebral Valley**, **Hugging Face**, **Patronus AI**, **Scale AI**, **Northflank**, **OpenPipe**, and **Unsloth AI** for the infrastructure and support. Personal thanks to **Ankit Maloo**.

---

*Multi-agent. Multi-mind. One office.*

