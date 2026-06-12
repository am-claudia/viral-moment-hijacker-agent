# Task 1 — DISCOVER: Search Viral Trends

## Agent: TrendResearchAgent

| Property | Value |
|---|---|
| **File** | `src/agents/trend_agent.py` |
| **Model** | `gemini-2.5-flash` |
| **Triggered by** | `search_viral_trends` tool call from the Orchestrator |
| **Type** | Single-turn sub-agent |

---

## What It Does

The TrendResearchAgent is the first step of the pipeline. It finds what's currently going viral on the target social platform within a given industry, then scores each trend for brand opportunity.

It runs in **two steps**:

1. **Scrape** — pulls live trending content from TikTok, Instagram, or LinkedIn via Apify
2. **Analyze** — sends the raw data to Gemini Flash, which ranks the top 3 trends by opportunity score and content angle

The Orchestrator never sees raw scraped data — it receives a clean, pre-analyzed report and can immediately pick the best trend to hijack.

---

## Inputs

Called by the Orchestrator via the `search_viral_trends` tool:

```json
{
  "industry": "food",
  "timeframe": "last 24 hours"
}
```

The `platform` parameter is injected by the tool dispatcher (from the Orchestrator's context), not passed by Gemini directly.

---

## Outputs

Returns a JSON string with the top 3 analyzed trends:

```json
{
  "industry": "food",
  "platform": "TikTok",
  "timeframe": "last 24 hours",
  "top_trends": [
    {
      "trend_name": "25-Day Gym Streak Challenge",
      "hashtag": "#gymstreak",
      "why_viral": "Creators are documenting daily gym visits with transformation content",
      "opportunity_score": 8,
      "content_angle": "Show how the right meal kit fuels a streak sustainably"
    }
  ]
}
```

---

## How It Works

```
search_viral_trends(industry, timeframe)
        │
        ▼
_SCRAPERS[platform](industry, count=10)   ← Apify API call
        │
        ▼
raw_trends (list of dicts with hashtags, views, captions)
        │
        ▼
client.models.generate_content(           ← Gemini Flash
    model = TREND_AGENT_MODEL,
    contents = raw_json,
    config = GenerateContentConfig(system_instruction="You are a viral trend analyst...")
)
        │
        ▼
Returns: JSON string → Orchestrator
```

### Platform Scrapers

| Platform | Apify Actor | Signal Used |
|---|---|---|
| TikTok | `clockworks/tiktok-scraper` | `playCount` (views) |
| Instagram | `apify/instagram-hashtag-scraper` | `likesCount` |
| LinkedIn | `scarletapi/linkedin-viral-posts-finder` | `reactionsCount` |

---

## Why This Design

- **Sub-agent, not raw tool**: The Orchestrator gets a ranked report, not raw hashtag lists. This keeps the Orchestrator focused on strategy, not data wrangling.
- **Flash model**: Structured JSON analysis of scraped data doesn't need Pro-level reasoning. Gemini Flash is fast and cheap.
- **Single-turn**: All context is available upfront (raw trends + industry). No back-and-forth needed.
