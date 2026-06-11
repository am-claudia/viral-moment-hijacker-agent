# Task 3 — STRATEGIZE: Choose the Brand Angle

## Agent: Orchestrator (ViralMomentHijacker)

| Property | Value |
|---|---|
| **File** | `src/agent.py` |
| **Model** | `claude-opus-4-8` with adaptive thinking |
| **Triggered by** | Internal reasoning after receiving TrendResearchAgent's report |
| **Type** | Orchestrator reasoning step (no tool call) |

---

## What It Does

After the TrendResearchAgent returns the top 3 viral trends, the Orchestrator picks the one most authentically aligned with the brand and decides on the specific angle to use.

This is a **pure reasoning step** — no tool is called. The Orchestrator thinks through:

- Which trend has the highest opportunity score
- Whether the brand connection feels authentic or forced
- What specific narrative angle the brand should take to enter the conversation
- Which trend to pick if the top-scoring one feels like a stretch

The result is a `brand_angle` string that flows into every subsequent task: DM pitches, the brand post, the content calendar, and the customer email.

---

## Inputs (from previous step)

The Orchestrator's conversation history already contains the TrendResearchAgent's JSON report:

```json
{
  "top_trends": [
    {
      "trend_name": "25-Day Gym Streak Challenge",
      "hashtag": "#gymstreak",
      "why_viral": "...",
      "opportunity_score": 8,
      "content_angle": "Show how the right meal kit fuels a streak sustainably"
    },
    ...
  ]
}
```

---

## Output (used in subsequent steps)

The Orchestrator's reasoning produces a brand angle that is passed to:
- Task 5 (`influencer_pitches`) — for personalizing DM copy
- Task 6 (`brand_post`) — for writing the reactive social post
- Task 7 (`generate_content_calendar`) — as the campaign theme
- Task 9 (`send_customer_email`) — as the `brand_angle` argument to the EmailAgent

Example brand angle:
> "Forkly is the brand that makes the gym streak sustainable — when your body is working hard, your kitchen shouldn't be. We provide the quick, nutritious meal kits that turn a 25-day streak into a 365-day lifestyle."

---

## System Prompt Guidance

The Orchestrator's system prompt directs this step explicitly:

```
3. STRATEGIZE — Choose the brand angle that feels most authentic.
   If the connection to {brand_name} seems forced, pick a different trend.
```

And the quality rules reinforce it:

```
Authenticity over virality — if the angle feels like a stretch, say so.
```

---

## Why This Design

- **No tool needed**: The Orchestrator already has all the data it needs (trend report in conversation history). Reasoning is faster than a round-trip tool call.
- **Adaptive thinking**: `claude-opus-4-8` with `thinking: {"type": "adaptive"}` and `output_config: {"effort": "high"}` lets the model decide how much to reason per step. Strategy selection benefits from this.
- **Authenticity gate**: The system prompt explicitly asks the model to flag forced connections. This prevents the agent from blindly hijacking an irrelevant trend just because it scored high.
