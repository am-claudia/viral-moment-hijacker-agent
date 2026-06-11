# Task 6 — CREATE: Write the Reactive Brand Post

## Agent: Orchestrator (ViralMomentHijacker)

| Property | Value |
|---|---|
| **File** | `src/agent.py` |
| **Model** | `claude-opus-4-8` with adaptive thinking |
| **Triggered by** | Internal reasoning after Tasks 3–5 are complete |
| **Type** | Orchestrator reasoning step (no tool call) |

---

## What It Does

The Orchestrator writes a single reactive brand post — the content the brand itself will publish on its own account to join the viral conversation. The post is platform-native, written in the brand's voice and tone, and directly tied to the chosen trend.

This is a **pure reasoning step** — the post is written in the Orchestrator's response and later passed to `post_to_social_media` (Task 8) and `save_campaign_results` (Task 10).

---

## Inputs (from previous steps)

The Orchestrator draws on:
- The chosen trend name + hashtag (Task 1)
- The brand angle (Task 3)
- The hashtag strategy (Task 4)
- The target platform and brand tone (from system prompt)

---

## Output

The `brand_post` string, written in the Orchestrator's response and passed to subsequent tools:

**Example (TikTok / casual tone):**
```
25 days. 25 dinners you actually looked forward to. 🌱🔥

The gym streak is the goal. Forkly is how you don't fall off between sessions.

Tag us in your streak meals 👇 #gymstreak #Forkly #mealkit #quickdinner
```

**Example (LinkedIn / professional tone):**
```
The #gymstreak challenge is showing us something we've always believed:
sustainable habits are built in the kitchen, not just the gym.

At Forkly, we exist for the moments between the workouts. 

What's fueling your streak this week?
```

---

## Platform Format Rules (from System Prompt)

The Orchestrator is told explicitly:

```
Brand post must fit {platform}'s native format and tone conventions.
```

Platform conventions:
| Platform | Expected format |
|---|---|
| TikTok | Short, punchy, emoji-heavy, hashtags inline, CTA to duet/stitch |
| Instagram | Visual-first caption, line breaks, hashtags at the end |
| LinkedIn | Conversational thought leadership, no hashtag spam, ends with a question |

---

## Why This Design

- **Orchestrator writes, not a sub-agent**: The brand post synthesizes everything decided so far — trend, brand angle, hashtags, platform format. A sub-agent would need all of that context injected artificially. The Orchestrator already has it.
- **One post, not a campaign**: The reactive post is a single piece of content that jumps on the moment. Volume and scheduling are handled in Task 7 (content calendar).
- **Tone enforcement**: The brand's `tone` value (e.g., "casual, witty, food-obsessed") is part of the system prompt, so every post the Orchestrator writes automatically inherits it.
