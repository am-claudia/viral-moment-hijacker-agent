# Task 10 — SAVE: Save Campaign Results

## Agent: Simulated Tool (no sub-agent)

| Property | Value |
|---|---|
| **File** | `src/tools.py` → `save_campaign_results()` |
| **Model** | None — pure Python function |
| **Triggered by** | `save_campaign_results` tool call from the Orchestrator |
| **Type** | Persistence function |

---

## What It Does

Assembles all campaign outputs into a single JSON file and writes supporting files for the content calendar and hashtag strategy. This is the **final step** — the Orchestrator calls it once with everything it has collected across the entire pipeline.

---

## Inputs

The Orchestrator passes the full campaign package gathered across all previous tasks:

```json
{
  "viral_trend": "25-Day Gym Streak Challenge",
  "trend_summary": "Fitness creators are documenting daily gym visits...",
  "brand_angle": "Forkly makes the gym streak sustainable...",
  "influencer_pitches": [
    {
      "name": "Jamie Torres",
      "handle": "@jamielifts",
      "followers": "145K",
      "dm_pitch": "Hey Jamie! Your Day 14 streak post..."
    }
  ],
  "brand_post": "25 days. 25 dinners you actually looked forward to...",
  "platform": "TikTok",
  "social_post_url": "https://www.tiktok.com/@brand/video/abc123xyz89",
  "customer_email_subject": "Your streak deserves the right fuel 🔥",
  "customer_email_subscribers": 14200,
  "content_calendar": [ ... 7 day objects ... ],
  "hashtag_strategy": { "groups": { ... }, "caption_formula": "..." }
}
```

---

## Outputs (Files Written)

### 1. Campaign JSON — `output/campaigns/campaign_<brand>_<timestamp>.json`

The full campaign package:

```json
{
  "metadata": {
    "brand": "Forkly",
    "platform": "TikTok",
    "generated_at": "2026-06-11T14:30:22"
  },
  "viral_trend": "...",
  "trend_summary": "...",
  "brand_angle": "...",
  "influencer_pitches": [ ... ],
  "brand_post": "...",
  "distribution": {
    "social_post_url": "https://www.tiktok.com/@brand/video/abc123",
    "customer_email_subject": "Your streak deserves the right fuel 🔥",
    "customer_email_subscribers": 14200
  },
  "content_calendar": [ ... ],
  "hashtag_strategy": { ... }
}
```

### 2. Calendar TXT — `output/calendars/calendar_<brand>_<timestamp>.txt`

Plain-text 7-day calendar for easy use by a social media manager.

### 3. Hashtags TXT — `output/hashtags/hashtags_<brand>_<timestamp>.txt`

Grouped hashtag sets with the caption formula.

---

## Return Value

```json
{
  "success": true,
  "saved_to": "output/campaigns/campaign_forkly_20260611_143022.json",
  "campaign_id": "forkly_20260611_143022"
}
```

The `saved_to` path is captured by the agentic loop in `agent.py` and used by `display_results()` in `main.py` to render the CLI summary.

---

## Why This Design

- **Single call at the end**: Rather than writing partial results at each step, the Orchestrator accumulates everything and saves once. This keeps the output atomic — either the full campaign is saved, or nothing is.
- **No sub-agent**: Saving files is deterministic. There is nothing for Gemini to reason about here.
- **Three output files**: The campaign JSON is the source of truth. The `.txt` files are convenience exports for the humans who will actually use the hashtags and calendar.
