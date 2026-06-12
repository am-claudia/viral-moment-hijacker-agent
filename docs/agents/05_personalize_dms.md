# Task 5 — PERSONALIZE: Write Influencer DM Pitches

## Agent: Orchestrator (ViralMomentHijacker)

| Property | Value |
|---|---|
| **File** | `src/agent.py` |
| **Model** | `gemini-2.5-pro` with built-in reasoning |
| **Triggered by** | Internal reasoning after `find_influencers` returns scored profiles |
| **Type** | Orchestrator reasoning step (no tool call) |

---

## What It Does

The Orchestrator writes a personalized DM pitch for each influencer identified in Task 2. This is a **pure reasoning step** — it draws on the InfluencerAgent's scored profiles and the brand angle from Task 3 to craft messages that feel human, not templated.

Each pitch uses three fields from the InfluencerAgent's output:
- `content_style` — the creator's posting style (e.g., "educational", "humorous")
- `why_good_fit` — why they're a strong match for this campaign
- `recent_trend_post` — what they actually posted about the trend

---

## Inputs (from previous steps)

The Orchestrator's conversation history contains:

**From Task 2 (InfluencerAgent):**
```json
{
  "influencers": [
    {
      "name": "Jamie Torres",
      "handle": "@jamielifts",
      "followers": "145K",
      "fit_score": 9,
      "why_good_fit": "Focuses on quick, healthy meals that fuel active lifestyles",
      "content_style": "educational",
      "recent_trend_post": "Day 14 of my gym streak and I finally cracked the meal prep code..."
    }
  ]
}
```

**From Task 3 (brand angle):**
> "Forkly makes the gym streak sustainable — quick, nutritious meal kits for people who are already putting in the work."

---

## Output

The `influencer_pitches` array written by the Orchestrator and later passed to `save_campaign_results`:

```json
[
  {
    "name": "Jamie Torres",
    "handle": "@jamielifts",
    "followers": "145K",
    "dm_pitch": "Hey Jamie! Your Day 14 streak post had me nodding — you nailed exactly why meal prep is the real cheat code. We're Forkly, a meal kit brand built for people who actually move their bodies. Would love to send you a week of kits to cook alongside your next streak milestone. No scripted content, just real food that fits your rhythm. Interested?"
  }
]
```

---

## Quality Rules (from System Prompt)

```
DMs must be warm, specific, and platform-native.
Use the influencer's content_style and recent_trend_post.
No "I came across your profile" openers.
```

The Orchestrator is explicitly told to avoid generic openers and to reference the creator's actual content.

---

## Why This Design

- **Orchestrator writes, not a sub-agent**: DM personalization requires synthesizing the brand angle, influencer fit data, and platform tone simultaneously. The Orchestrator has all of this in its context window.
- **Grounded in real data**: The `recent_trend_post` field (from actual TikTok scraping) gives the Orchestrator something concrete to reference in each pitch — making the message feel genuine.
- **Adaptive thinking earns its keep here**: Writing three distinct, human-sounding DMs for different creator personalities is exactly the kind of multi-step creative task where Opus's reasoning depth matters.
