# Viral Moment Hijacker — Project Spec

## Overview

AI marketing agent that monitors viral moments in a target industry, identifies relevant influencers, crafts personalized DM pitches, and generates a reactive brand post — all in one automated pipeline.

**University Assignment:** Agentic AI Systems with Tool Use  
**Tech Stack:** Python 3.11+, Anthropic Claude API (claude-opus-4-8), Rich CLI

---

## Architecture

```
main.py (CLI)
    │
    └── ViralMomentHijacker (src/agent.py)
            │
            ├── Orchestrator: claude-opus-4-8 with adaptive thinking
            │
            └── Tools (src/tools.py)
                    ├── search_viral_trends()   → simulates trend API
                    ├── find_influencers()       → simulates influencer API
                    └── save_campaign_results()  → persists output to JSON
```

The agent uses Claude's tool_use API pattern: Claude decides when to call each tool, processes the results, and synthesizes all creative outputs (brand angle, DM pitches, brand post) through its own reasoning.

---

## Agent Workflow

```
1. DISCOVER  → search_viral_trends(industry, timeframe)
                Returns ranked trending topics with sentiment + opportunity data

2. IDENTIFY  → find_influencers(trend, platform, niche)
                Returns influencer profiles: followers, engagement, recent content

3. STRATEGIZE (Claude reasoning)
                Picks the best angle for the brand to authentically join the conversation

4. PERSONALIZE (Claude reasoning)
                Drafts platform-native DM pitches referencing each influencer's actual content

5. CREATE (Claude reasoning)
                Generates reactive brand post optimized for the target platform

6. SAVE      → save_campaign_results(campaign_data)
                Writes full campaign package to output/<brand>_<timestamp>.json
```

---

## Tool Definitions

### `search_viral_trends`
**Purpose:** Discovers what's going viral in the target industry right now.  
**Inputs:** `industry` (str), `timeframe` ("last 24 hours" | "last 48 hours" | "this week")  
**Returns:** JSON with trending topics, hashtags, estimated post counts, sentiment, and opportunity level.  
**Production integration:** Replace mock data with Twitter API v2, Google Trends API, TikTok Research API, Reddit API.

### `find_influencers`
**Purpose:** Finds influencers actively posting about the chosen trend.  
**Inputs:** `trend` (str), `platform` (str), `niche` (str), `count` (int, default 3)  
**Returns:** JSON array of influencer profiles with follower counts, engagement rates, content style, and recent trend-related posts.  
**Production integration:** HypeAuditor API, Modash API, or direct platform APIs.

### `save_campaign_results`
**Purpose:** Persists the complete campaign to disk for review and sharing.  
**Inputs:** `viral_trend`, `trend_summary`, `brand_angle`, `influencer_pitches[]`, `brand_post`, `platform`  
**Returns:** JSON with save path and campaign ID.  
**Output location:** `output/campaign_<brand>_<timestamp>.json`

---

## Key Design Decisions

**Why claude-opus-4-8 with adaptive thinking?**  
The campaign strategy (angle selection, DM personalization, post creation) requires multi-step reasoning about brand fit, trend context, and audience psychology. Adaptive thinking lets Claude decide how deeply to reason about each step.

**Why a manual agentic loop over the tool runner?**  
The manual loop (in `agent.py`) gives us full control to log each tool call, inject context (brand name for the save tool), and handle progress display. The tool runner would work too but hides intermediate steps.

**Why mock data tools instead of real APIs?**  
Real social media APIs require business accounts and rate limits that complicate a university demo. The mock tools (backed by a fast claude-haiku-4-5 call) generate realistic, industry-specific data. Production migration = swap the function bodies.

**Why separate roles for haiku vs opus?**  
Data generation (mock trends/influencers) uses `claude-haiku-4-5` — fast and cheap for structured JSON output. Strategic synthesis (angle, DMs, post) is handled by the orchestrating `claude-opus-4-8` through its own reasoning, not as tool calls.

---

## Project Structure

```
viral-moment-hijacker-agent/
├── CLAUDE.md          ← this file (project spec)
├── README.md          ← setup and usage instructions
├── requirements.txt   ← Python dependencies
├── .env.example       ← required environment variables
├── main.py            ← CLI entry point
├── src/
│   ├── __init__.py
│   ├── config.py      ← loads .env config
│   ├── tools.py       ← tool schemas + implementations
│   └── agent.py       ← orchestrator + agentic loop
└── output/            ← generated campaign JSON files
```

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | Yes | Anthropic API key from console.anthropic.com |

---

## Development Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Copy and fill environment variables
cp .env.example .env

# Run a demo campaign
python main.py \
  --industry fitness \
  --brand-name "ActiveWear Co" \
  --brand-description "Sustainable activewear for everyday athletes" \
  --platform Instagram \
  --tone casual

# Run with all options
python main.py \
  --industry fintech \
  --brand-name "PayFlow" \
  --brand-description "B2B payment processing startup" \
  --platform LinkedIn \
  --brand-values "transparent, founder-friendly, no hidden fees" \
  --tone professional
```

---

## Output Format

Each campaign is saved to `output/campaign_<brand>_<timestamp>.json`:

```json
{
  "metadata": {
    "brand": "ActiveWear Co",
    "platform": "Instagram",
    "generated_at": "2026-06-05T14:30:00"
  },
  "viral_trend": "25-Day Gym Streak Challenge",
  "trend_summary": "Fitness creators are documenting 25-day gym streaks...",
  "brand_angle": "Provide the gear that makes the streak sustainable...",
  "influencer_pitches": [
    {
      "name": "Jamie Torres",
      "handle": "@jamielifts",
      "followers": "145K",
      "dm_pitch": "Hey Jamie! Saw your 25-day streak content..."
    }
  ],
  "brand_post": "25 days. 25 different fits. One sustainable wardrobe. 🌱💪 #GymStreak"
}
```

---

## Extending the Agent

**Add a real trend source:** Edit `search_viral_trends()` in `src/tools.py`. Replace the Claude mock call with your chosen API. Keep the same return format (JSON string).

**Add more influencer filters:** Add parameters to `find_influencers()` (e.g., `min_followers`, `max_followers`, `verified_only`).

**Add email/DM sending:** Add a `send_dm()` tool that integrates with a platform API. Add its schema to `TOOL_SCHEMAS` and handle it in `agent._execute_tool()`.

**Change the model:** Update `model` in `src/config.py`. The pipeline works with any Claude model that supports tool_use.
