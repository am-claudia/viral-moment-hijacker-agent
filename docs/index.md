---
layout: default
---

> An AI multi-agent system that monitors what's going viral in any industry, identifies the right creators, writes personalized outreach, publishes a reactive brand post, and emails your customers — all from a single command.

---

## The problem

When a trend blows up, brands that win respond within **hours, not days**. The manual workflow kills you: monitor platforms → find creators → research each one → write personalized outreach → draft a post → notify customers. By the time that's done, the moment has passed.

This agent runs the entire workflow automatically.

---

## How it works

The system is built as an **orchestrator + 3 specialized sub-agents**. Each agent has one job and the right model for it.

| Agent | Model | Job |
|---|---|---|
| **Orchestrator** | Gemini 2.5 Flash | Strategy, brand angle, DM pitches, brand post, calendar |
| **TrendResearchAgent** | Gemini 2.5 Flash | Scrape Apify live data → rank trends by opportunity score |
| **InfluencerAgent** | Gemini 2.5 Flash | Scrape creator profiles → score each on niche fit |
| **EmailAgent** | Gemini 2.5 Flash | Write full customer email from trend context → simulate send |

```
Orchestrator (Gemini 2.5 Flash)
    │
    ├── search_viral_trends  →  TrendResearchAgent
    │                           Scrapes Apify, returns ranked trends with content angles
    │
    ├── find_influencers     →  InfluencerAgent
    │                           Scrapes creator profiles, returns fit scores + why_good_fit
    │
    └── send_customer_email  →  EmailAgent
                                Writes subject, body, CTA — orchestrator never touches email copy
```

The orchestrator receives **pre-analyzed reports**, not raw scraped data — so it can focus entirely on strategy.

---

## 10-step pipeline

| Step | Task | Agent |
|---|---|---|
| 1 — DISCOVER | Scrape live trending content from TikTok / Instagram / LinkedIn | TrendResearchAgent |
| 2 — IDENTIFY | Score real creator profiles for niche fit | InfluencerAgent |
| 3 — STRATEGIZE | Pick the most authentic brand angle | Orchestrator |
| 4 — HASHTAGS | Generate grouped hashtag strategy (broad / niche / branded / trend) | Orchestrator |
| 5 — PERSONALIZE | Write a custom DM pitch per creator using their actual content style | Orchestrator |
| 6 — CREATE | Write a reactive brand post in the brand's voice | Orchestrator |
| 7 — CALENDAR | Build a 7-day content plan (Day 1 jumps on trend, Days 6–7 convert) | Orchestrator |
| 8 — POST | Publish the brand post to social media | Simulated tool |
| 9 — EMAIL | Write and send a trend-inspired customer email | EmailAgent |
| 10 — SAVE | Write the full campaign package to `output/` as timestamped JSON | Python function |

---

## Agent documentation

Each step has its own detailed doc covering inputs, outputs, how it works, and design decisions.

- [Orchestrator](agents/00_orchestrator.md) — agentic loop, system prompt, tool delegation
- [Task 1 — Discover Trends](agents/01_discover_trends.md)
- [Task 2 — Identify Influencers](agents/02_identify_influencers.md)
- [Task 3 — Strategize](agents/03_strategize.md)
- [Task 4 — Hashtag Strategy](agents/04_hashtag_strategy.md)
- [Task 5 — Personalize DMs](agents/05_personalize_dms.md)
- [Task 6 — Create Brand Post](agents/06_create_brand_post.md)
- [Task 7 — Content Calendar](agents/07_content_calendar.md)
- [Task 8 — Post to Social Media](agents/08_post_social_media.md)
- [Task 9 — Customer Email](agents/09_customer_email.md)
- [Task 10 — Save Campaign](agents/10_save_campaign.md)

---

## Quick start

```bash
# Install dependencies
pip install -r requirements.txt

# Add your API keys to .env
cp .env.example .env

# Run a campaign
python main.py \
  --industry food \
  --brand-name "Forkly" \
  --brand-description "Fun meal kit brand for millennials and Gen Z" \
  --platform TikTok \
  --tone "casual, witty"
```

**Required API keys:**
- `GEMINI_API_KEY` — from [aistudio.google.com](https://aistudio.google.com) (free)
- `APIFY_API_TOKEN` — from [apify.com](https://apify.com) (free tier available)

---

## Output

Every campaign run saves 4 files to `output/`:

| File | Contents |
|---|---|
| `campaigns/<brand>_<timestamp>.json` | Full campaign package — trend, pitches, post, email, calendar, hashtags |
| `calendars/<brand>_<timestamp>.txt` | 7-day content calendar as plain text |
| `hashtags/<brand>_<timestamp>.txt` | Grouped hashtag sets + caption formula |
| `emails/email_<timestamp>.txt` | Customer email preview |

---

## Tech stack

- **AI** — Google Gemini 2.5 Flash (all agents)
- **Scraping** — Apify (TikTok, Instagram, LinkedIn)
- **CLI** — Python 3.11+ with Rich for terminal UI
- **Pattern** — Manual agentic loop with tool use
