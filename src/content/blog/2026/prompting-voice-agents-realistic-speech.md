---
title: "How to Make Voice Agents Sound Human: A Practical Guide to Realistic Speech Prompting"
description: "Why your cascaded voice agent sounds robotic — and how to fix it with concrete examples, SSML pause patterns, emotion tags, and personality-as-behavior prompting techniques."
pubDatetime: 2026-04-03T00:00:00Z
tags:
  - voice-ai
  - agents
  - prompting
  - llm
  - tts
featured: true
---

Every voice AI developer eventually hits the same wall: the agent works, it's fast, it's accurate — but it sounds like a Wikipedia article being read aloud. The words are right. The *feel* is completely wrong.

This is the uncanny valley of voice AI, and it's not a model problem. It's a prompting problem.

<div style="position:relative;padding-bottom:56.25%;height:0;overflow:hidden;margin:2rem 0;">
  <iframe src="https://www.youtube.com/embed/FBSam25u8O4" style="position:absolute;top:0;left:0;width:100%;height:100%;border:0;" allowfullscreen></iframe>
</div>

## The S2S vs. Cascade Debate (and Why It's the Wrong Question)

One of the most common questions in voice AI right now: *"Should I use a speech-to-speech model or the cascade pipeline (STT → LLM → TTS)?"*

What developers are really asking is: **how do I make my agent sound human?**

Here's the thing — a cascaded pipeline can match S2S latency these days, and it's significantly more reliable at tool calling. But left to its defaults, it produces something unmistakable: *written language read out loud*.

Look no further than Anthropic's recent Super Bowl commercial for a textbook example of what happens when polished LLM prose meets a TTS engine.

The root cause is simple: LLMs are trained on mountains of text and post-trained to produce clean, grammatically correct writing. That's perfect for chatbots and emails. But **humans don't talk the way they write**. Real speech is full of filler words, mid-sentence corrections, little laughs, soft pauses, and sentences that wander.

So yes, the fix is "prompt it to be more natural." But in practice, the model will **fight you** unless you're extremely explicit.

## Step 1: Define Natural Speech with Concrete Examples

Vague style instructions don't work. If you tell an LLM to "be conversational," it will still produce polished prose with marginally shorter sentences. You need to **show** the model what you mean.

Here's a prompt that *sounds* reasonable but won't produce realistic speech:

```
You are a customer support agent. You are brief with your responses.
You use filler words too much, which are symbolized by "uhs" and "ums".
This is okay. It is natural.
Your goal is natural, super conversational spoken exchanges.
Keep it short, usually one sentence, and remember you are imperfect.
```

This fails because there's nothing concrete to latch onto. Instead, **write out actual example sentences** your agent should produce:

> **Bad version:** "I can definitely handle that for you."
> **Your version:** "Yeah, um so, I can do that, no problem."

> **Bad version:** "Unfortunately I'm going to have to cancel your service."
> **Your version:** "So... um so... we're unfortunately going to have to cancel."

These examples teach the LLM not just *that* it should use filler words, but *how* to structure them in real sentences — where they go, how they cluster, what words follow them.

**Pro tip:** If you have call recordings between customers and human agents, mine them for speech patterns. Real human speech is the best training data for your system prompt.

## Step 2: Engineer Disfluencies with Structured Pause Patterns

Filler words alone aren't enough. What makes them feel real is **timing**.

When humans say "um," they generally pause briefly, then restart with a connector like "so." Agents often miss this — they say "um" and then blast forward at full speed, which instantly reads as fake.

If your TTS engine supports SSML tags, you can teach the model to embed pause instructions directly in its output:

```
WHAT GOOD OUTPUT LOOKS LIKE:

Bad version: "I can definitely handle that for you."
Your version: Yeah, um <break time="300ms"/> so <break time="300ms"/>,
  I can do that, <break time="300ms"> no problem.

Bad version: "Unfortunately I'm going to have to cancel your service."
Your version: So <break time="300ms"/> um <break time="300ms"/>
  so <break time="300ms"/> we're unfortunately going to have to cancel.
```

The magic is that the LLM generates these pause markers, and the downstream TTS engine interprets them as actual pauses in the audio. The result sounds dramatically more natural.

### Reinforce the Pattern from Multiple Angles

This is the key insight that separates good voice prompts from great ones. **State the same rule in three different ways:**

**1. State it explicitly:**
```
After every standalone "um", immediately insert <break time="300ms"/>.
```

**2. Show examples:**
```
Yeah, um <break time="300ms"/> so <break time="300ms"/>, sure I can do that.
```

**3. Restate it in an emphasis section:**
```
LEAN INTO THIS HARD:
Everything below is essential. You are mid-conversation at a coffee
shop, not presenting a keynote:
- Filler words are good: "um," "so," "okay," "hm," "like," "ya so"
- If you use "um", make sure you always follow up with a "so"
  after the pause!
```

The model almost always needs **more redundancy than you expect**. If you think you've repeated it enough, repeat it one more time.

## Step 3: Treat Emotion Tags as Constraints, Not Decorations

Emotion controls in TTS engines work best when used as **guardrails**, not paint.

Humans don't ping-pong between emotions mid-sentence. If your agent goes from excited to amused to sad to angry in one turn, it sounds unstable, not expressive.

**Two rules that dramatically improve realism:**

1. **Default to calm.** Tags like `peaceful` sound more human than `excited`. Set your baseline low and let specific scenarios earn stronger emotions.

2. **Map emotions to specific triggers**, not general vibes:

```
VOCAL COLOR THROUGH AUTHENTIC REACTIONS:

- Default state:
  <emotion value="peaceful" /> Ya, okay so I can help with that.

- High energy (use sparingly):
  <emotion value="happy" /> Yeah <break time="300ms"/>,
  I totally get that

- Amusement through calm:
  <emotion value="peaceful" /> [laughter] Okay that is really funny

- Sad moments with pauses:
  <emotion value="sad" /> Yeah... um <break time="300ms"/>
  so ... I'm really sorry about that

- Narrate lookups out loud:
  Hmm, let me just check that <break time="500ms">.
  Ooone second here, <break time="300ms">
  Just looking at it for you.
```

That last pattern — **narrating lookups** — is incredibly effective. When a human agent puts you on hold, they don't go silent. They say "let me pull that up" or "one second, checking now." Your AI agent should do the same.

## Step 4: Write Personality as Audible Behaviors, Not Adjectives

"Friendly and helpful" is already the default mode of every LLM on the planet. If you want distinct, realistic personality, you need traits that map to **observable speech patterns** — things the model can literally output.

Here's what actually works:

```
You carry a steady, positive energy without being syrupy about it.
There is a chill confidence underneath everything. Your default
gear is relaxed enthusiasm.

Break grammar rules. Start sentences with "And," "But," or "So."
Use "like" often.

Loop back without referring to the specific subject when you need
to go back: "About that other thing you mentioned"

Pauses are fine; when you fill them, use "ya" <break time="300ms"/>,
or "so yeah", or "anyway".

Whenever you say "um" then a <break>, pick up again with "so"
after the pause.

If confused or you think you misheard something:
"Sorry, <break time="300ms"/>, I think I missed that, what did
you say?"

When the customer says goodbye, wish them a good day!
```

Each line here is something the model can directly execute. "Break grammar rules" → start sentences with "And." "Chill confidence" → "relaxed enthusiasm" as a default gear. Abstract adjectives become concrete speech acts.

## The Complete System Prompt Pattern

Putting it all together, a realistic voice agent system prompt follows this structure:

```
1. ROLE & CONTEXT
   Who you are, what you do, who you're talking to

2. SPEECH EXAMPLES (most important section)
   5-10 "bad version → your version" pairs
   covering greetings, questions, apologies, lookups, goodbyes

3. PAUSE RULES
   Explicit SSML rules stated, then shown, then restated

4. EMOTION GUIDELINES
   Default baseline + specific trigger scenarios

5. PERSONALITY BEHAVIORS
   Concrete speech patterns, not adjective lists

6. REINFORCEMENT SECTION
   "LEAN INTO THIS HARD:" — restate the 3 most important
   behaviors one final time
```

## Why This Works: The Redundancy Principle

LLMs are instruction-following machines trained on massive text corpora. Their default gravitational pull is toward clean, well-structured prose. To overcome that pull, you need **escape velocity** — and escape velocity in prompting means repetition from different angles.

A single instruction like "use filler words" gets acknowledged but quickly overridden by the model's training. The same instruction stated as a rule, shown in 5 examples, restated in an emphasis section, and reinforced in personality guidelines? That sticks.

Think of it like CSS specificity — the more selectors that point to the same style, the more likely it wins.

## Common Pitfalls

| Pitfall | What happens | Fix |
|---------|-------------|-----|
| Only vague instructions | Model ignores them within 2 turns | Add 5+ concrete examples |
| Filler words without pauses | Sounds like "um" was randomly injected | Pair every "um" with `<break>` tags |
| Too many emotion switches | Agent sounds manic | Default to `peaceful`, allow 2-3 specific triggers |
| No narrated lookups | Awkward silence during tool calls | Add "let me check" + pause patterns |
| Personality as adjectives | Generic LLM personality | Rewrite as audible speech behaviors |
| Not enough redundancy | Model drifts back to formal within 3-4 turns | State each rule 3x from different angles |

## The Takeaway

If your voice agent sounds robotic, **look at your system prompt before you blame your model or TTS engine.** The cascaded pipeline is perfectly capable of producing natural, human-sounding speech. The bottleneck is almost always in how you instruct the LLM.

Stuff the prompt with examples. Be surgical about disfluencies. Pair "um" with pauses and recovery words. Reinforce the same rule from multiple angles. Define personality as behaviors you can hear.

And when you think you've repeated it enough times — repeat it again. The model always needs more redundancy than you expect.

---

*This post distills techniques from the voice AI community, particularly insights shared by the [LiveKit](https://livekit.io/) team. If you're building voice agents, their [open-source framework](https://github.com/livekit/agents) is worth exploring.*
