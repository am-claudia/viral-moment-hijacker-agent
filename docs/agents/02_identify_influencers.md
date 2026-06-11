# Task 2 — IDENTIFY: Find Influencers

## Agent: InfluencerAgent

| Property | Value |
|---|---|
| **File** | `src/agents/influencer_agent.py` |
| **Model** | `claude-haiku-4-5-20251001` |
| **Triggered by** | `find_influencers` tool call from the Orchestrator |
| **Type** | Single-turn sub-agent |

---

## What It Does

The InfluencerAgent identifies and evaluates real creators who are actively posting about the chosen viral trend. It doesn't just return a list of names — it scores each creator on niche fit and engagement quality so the Orchestrator can write truly personalized DM pitches.

It runs in **two steps**:

1. **Scrape** — pulls real creator profiles from TikTok via Apify who are posting about the trend hashtag
2. **Score** — sends raw profiles to Claude Haiku, which evaluates each creator and returns the top matches ranked by `fit_score`

---

## Inputs

Called by the Orchestrator via the `find_influencers` tool:

```json
{
  "trend": "#gymstreak",
  "platform": "TikTok",
  "niche": "home cooking",
  "count": 3
}
```

---

## Outputs

Returns a JSON string with ranked, scored creator profiles:

```json
{
  "trend": "#gymstreak",
  "platform": "TikTok",
  "niche": "home cooking",
  "influencers": [
    {
      "name": "Jamie Torres",
      "handle": "@jamielifts",
      "followers": "145K",
      "verified": false,
      "platform": "TikTok",
      "fit_score": 9,
      "why_good_fit": "Focuses on quick, healthy meals that fuel active lifestyles — perfect alignment with the streak angle",
      "content_style": "educational",
      "recent_trend_post": "Day 14 of my gym streak and I finally cracked the meal prep code..."
    }
  ]
}
```

The `fit_score`, `why_good_fit`, and `content_style` fields are used directly by the Orchestrator when writing DM pitches in Task 5.

---

## How It Works

```
find_influencers(trend, platform, niche, count)
        │
        ▼
_scrape_tiktok_creators(trend, count * 3)   ← Apify API call
        │  (sorted by followers_raw, top count*2 kept)
        ▼
raw_creators (list of dicts with handle, bio, video stats)
        │
        ▼
anthropic.messages.create(                   ← Claude Haiku
    model = INFLUENCER_AGENT_MODEL,
    system = "You are an influencer marketing analyst...",
    messages = [{ "role": "user", "content": raw_json }]
)
        │
        ▼
Returns: JSON string → Orchestrator
```

### What the Scraper Collects

From `clockworks/tiktok-scraper` (30 results per hashtag):

| Field | Source |
|---|---|
| `name` | `authorMeta.nickName` |
| `handle` | `authorMeta.name` |
| `followers_raw` | `authorMeta.fans` |
| `bio` | `authorMeta.signature` (first 150 chars) |
| `recent_trend_post` | `text` (first 200 chars) |
| `video_views` | `playCount` |
| `video_likes` | `diggCount` |

Duplicates are removed (by handle). Creators are sorted by follower count before being sent to Claude.

---

## Why This Design

- **Real profiles, not fabricated**: Apify scrapes actual TikTok data — the Orchestrator writes DMs based on real bios and recent posts.
- **Scored profiles, not raw lists**: The `fit_score` and `content_style` fields make personalization easy. The Orchestrator uses them directly in Task 5.
- **Haiku model**: Scoring and ranking structured profile data is a classification task — Haiku handles it well at low cost.
- **Only TikTok for now**: Instagram and LinkedIn scrapers are not yet implemented. See `CLAUDE.md` → Extending the Agent for how to add them.
