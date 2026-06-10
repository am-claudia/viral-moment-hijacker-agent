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
            │   Handles: strategy, brand angle, DM pitches, brand post
            │
            └── Tools (src/tools.py)  ← each tool dispatches to a sub-agent or runs directly
                    │
                    ├── search_viral_trends()   → TrendResearchAgent  (claude-haiku-4-5)
                    │                              Scrapes Apify + analyzes opportunities
                    │
                    ├── find_influencers()       → InfluencerAgent     (claude-haiku-4-5)
                    │                              Scrapes Apify + scores creator fit
                    │
                    ├── send_customer_email()   → EmailAgent           (claude-sonnet-4-6)
                    │                              Writes full email + simulates sending
                    │
                    ├── post_to_social_media()  → simulated (no sub-agent needed)
                    ├── generate_hashtag_strategy() → pass-through formatter
                    ├── generate_content_calendar() → pass-through formatter
                    └── save_campaign_results() → persists output to JSON
```

**Multi-agent pattern:** The orchestrator calls tools like normal. What changed is that three of those tools now spin up their own Claude API call — a specialized sub-agent with a focused system prompt — instead of running a Python function. The orchestrator never sees the difference.

---

## Agent Workflow

```
1. DISCOVER  → search_viral_trends(industry, timeframe)
                TrendResearchAgent scrapes Apify live data, then analyzes
                and ranks trends by opportunity score + content angle.

2. IDENTIFY  → find_influencers(trend, platform, niche)
                InfluencerAgent scrapes Apify creator profiles, then scores
                each on niche fit and returns ranked matches with why_good_fit.

3. STRATEGIZE (Orchestrator reasoning)
                Picks the best angle for the brand to authentically join the conversation.

4. HASHTAGS  → generate_hashtag_strategy(broad, niche, branded, trend, formula)
                Orchestrator writes the hashtags; this tool formats and returns them.

5. PERSONALIZE (Orchestrator reasoning)
                Writes custom DM pitches using the InfluencerAgent's fit scores and
                content_style data — no generic "I came across your profile" openers.

6. CREATE (Orchestrator reasoning)
                Writes a reactive brand post optimized for the target platform.

7. CALENDAR  → generate_content_calendar(days[])
                Orchestrator writes the 7-day plan; this tool formats and returns it.

8. POST      → post_to_social_media(platform, post_content)
                Simulates publishing the post. Returns post URL + estimated reach.

9. EMAIL     → send_customer_email(trend_name, trend_summary, brand_angle)
                EmailAgent writes the full email (subject, body, CTA) and simulates
                sending it. Orchestrator does NOT write the email copy itself.

10. SAVE     → save_campaign_results(all fields)
                Writes full campaign package to output/campaigns/<brand>_<timestamp>.json
                Also writes calendar TXT and hashtags TXT to their own output folders.
```

---

## Sub-Agent Definitions

### TrendResearchAgent (`src/agents/trend_agent.py`)
**Model:** `claude-haiku-4-5-20251001`  
**Triggered by:** `search_viral_trends` tool call  
**What it does:**
1. Scrapes live trending content from TikTok / Instagram / LinkedIn via Apify
2. Passes raw data to Claude, which ranks the top 3 trends by opportunity score  

**Returns:** `{ top_trends: [{ trend_name, hashtag, why_viral, opportunity_score, content_angle }] }`  
**Why a sub-agent?** The orchestrator gets a pre-analyzed report (not raw hashtags) so it can focus on strategy, not data interpretation.

---

### InfluencerAgent (`src/agents/influencer_agent.py`)
**Model:** `claude-haiku-4-5-20251001`  
**Triggered by:** `find_influencers` tool call  
**What it does:**
1. Scrapes real creator profiles from TikTok via Apify
2. Passes raw profiles to Claude, which scores each on niche fit and engagement quality  

**Returns:** `{ influencers: [{ name, handle, followers, fit_score, why_good_fit, content_style, recent_trend_post }] }`  
**Why a sub-agent?** Returns scored profiles — the orchestrator uses `content_style` and `why_good_fit` directly when writing DM pitches.

---

### EmailAgent (`src/agents/email_agent.py`)
**Model:** `claude-sonnet-4-6`  
**Triggered by:** `send_customer_email` tool call  
**What it does:**
1. Receives trend context + brand info (injected from the ViralMomentHijacker instance)
2. Claude writes a complete email: subject, body, featured item, CTA
3. Simulates sending and saves a preview to `output/emails/`  

**Returns:** `{ subject, email_body, featured_item, cta_text, subscribers_reached, estimated_open_rate, ... }`  
**Why a sub-agent?** Email copywriting is a distinct creative task. Delegating it keeps the orchestrator focused on campaign strategy, not email formatting. Uses Sonnet (not Haiku) because copy quality matters.

---

## Key Design Decisions

**Why claude-opus-4-8 with adaptive thinking for the orchestrator?**  
Campaign strategy requires multi-step reasoning: picking the right brand angle, personalizing DMs for each influencer, and writing platform-native content. Adaptive thinking lets Claude decide how deeply to reason per step.

**Why a manual agentic loop?**  
The manual loop in `agent.py` gives full visibility into each tool call (name, args, result), injects brand context that can't come from the orchestrator's prompt alone, and drives the Rich progress display. An auto-runner would hide these steps.

**Why different models per sub-agent?**  
- Haiku (Trend + Influencer agents): fast and cheap for structured JSON analysis of scraped data.  
- Sonnet (Email agent): better creative writing for customer-facing copy.  
- Opus (Orchestrator): best reasoning for multi-step strategy and personalization.

**Why do sub-agents use single-turn calls (no loop)?**  
Each sub-agent has one focused job with all context available upfront — no back-and-forth needed. A loop would add latency and complexity for no benefit. Loops are for tasks that require tool use themselves.

**Why inject brand context in `execute_tool` rather than the orchestrator's prompt?**  
`brand_description` and `tone` are needed by the EmailAgent but should not be in every tool call's input schema — that would be noise. The dispatcher (`execute_tool`) injects them from the `ViralMomentHijacker` instance at call time.

---

## Project Structure

```
viral-moment-hijacker-agent/
├── CLAUDE.md              ← this file (project spec)
├── README.md              ← setup and usage instructions
├── requirements.txt       ← Python dependencies
├── .env.example           ← required environment variables
├── main.py                ← CLI entry point
├── src/
│   ├── __init__.py
│   ├── config.py          ← model constants (orchestrator + 3 sub-agents)
│   ├── tools.py           ← tool schemas + dispatcher (delegates to sub-agents)
│   ├── agent.py           ← orchestrator + agentic loop
│   └── agents/
│       ├── __init__.py    ← exports run_trend_agent, run_influencer_agent, run_email_agent
│       ├── trend_agent.py     ← TrendResearchAgent
│       ├── influencer_agent.py← InfluencerAgent
│       └── email_agent.py     ← EmailAgent
└── output/
    ├── campaigns/         ← full campaign JSON files
    ├── calendars/         ← 7-day calendar TXT files
    ├── hashtags/          ← hashtag strategy TXT files
    └── emails/            ← customer email preview TXT files
```

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | Yes | Anthropic API key from console.anthropic.com |
| `APIFY_API_TOKEN` | Yes | Apify token for live social media scraping |

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

Campaigns are saved to `output/campaigns/campaign_<brand>_<timestamp>.json`:

```json
{
  "metadata": { "brand": "ActiveWear Co", "platform": "Instagram", "generated_at": "..." },
  "viral_trend": "25-Day Gym Streak Challenge",
  "trend_summary": "Fitness creators are documenting 25-day gym streaks...",
  "brand_angle": "Provide the gear that makes the streak sustainable...",
  "influencer_pitches": [
    { "name": "Jamie Torres", "handle": "@jamielifts", "followers": "145K", "dm_pitch": "Hey Jamie!..." }
  ],
  "brand_post": "25 days. 25 different fits. 🌱💪 #GymStreak",
  "distribution": {
    "social_post_url": "https://www.instagram.com/p/abc123/",
    "customer_email_subject": "Your streak deserves the right gear",
    "customer_email_subscribers": 14200
  },
  "content_calendar": [...],
  "hashtag_strategy": { "groups": { "broad": [...], "niche": [...], ... } }
}
```

---

## Extending the Agent

**Add a new sub-agent:** Create `src/agents/your_agent.py` with a `run_your_agent()` function. Export it from `src/agents/__init__.py`. Call it from the relevant tool function in `src/tools.py`.

**Swap a sub-agent's model:** Change `TREND_AGENT_MODEL`, `INFLUENCER_AGENT_MODEL`, or `EMAIL_AGENT_MODEL` in `src/config.py`.

**Add Instagram/LinkedIn influencer scraping:** `InfluencerAgent` currently only scrapes TikTok. Add `_scrape_instagram_creators()` and `_scrape_linkedin_creators()` to `src/agents/influencer_agent.py` following the same pattern as `_scrape_tiktok_creators()`.

**Add a real email sender:** In `src/agents/email_agent.py`, replace the simulated send block with a call to SendGrid, Mailchimp, or Klaviyo. The email content is already written by Claude — just pass it to the API.
