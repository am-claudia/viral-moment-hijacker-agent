---
layout: default
title: Viral Moment Hijacker
---

# Viral Moment Hijacker

> An AI agent that monitors what's going viral in any industry, finds the right creators, writes personalized outreach, publishes a reactive brand post, and emails your customers — all from a single command.

---

## The problem it solves

When a trend blows up, brands that win respond within **hours, not days**. The manual workflow is too slow — by the time you've monitored platforms, found creators, researched each one, written outreach, drafted a post, and notified customers, the moment has passed.

This agent runs the entire workflow in one automated pipeline.

---

## Multi-agent architecture

```
Claude Opus 4.8 (Orchestrator)
    │
    ├── search_viral_trends  →  TrendResearchAgent  (Haiku)
    │                           Scrapes Apify live data, ranks trends by opportunity score
    │
    ├── find_influencers     →  InfluencerAgent     (Haiku)
    │                           Scrapes creator profiles, scores each on niche fit
    │
    └── send_customer_email  →  EmailAgent          (Sonnet)
                                Writes the full email from trend context, simulates send
```

The orchestrator never writes the email itself — it delegates with just trend context and gets back a confirmation. Same for trends and influencers: it receives analyzed reports, not raw scraped data, so it can focus entirely on strategy.

---

## 10-step pipeline

| # | Task | Who does it |
|---|---|---|
| 1 | Scrape live trending content | TrendResearchAgent (Haiku) |
| 2 | Score real creator profiles | InfluencerAgent (Haiku) |
| 3 | Pick the authentic brand angle | Orchestrator (Opus) |
| 4 | Generate hashtag strategy | Orchestrator (Opus) |
| 5 | Write personalized DM pitches | Orchestrator (Opus) |
| 6 | Write the reactive brand post | Orchestrator (Opus) |
| 7 | Build a 7-day content calendar | Orchestrator (Opus) |
| 8 | Publish to social media | Simulated tool |
| 9 | Write and send customer email | EmailAgent (Sonnet) |
| 10 | Save the full campaign package | Python function |

---

## Agent docs

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
pip install -r requirements.txt
cp .env.example .env   # add ANTHROPIC_API_KEY + APIFY_API_TOKEN

python main.py \
  --industry food \
  --brand-name "Forkly" \
  --brand-description "Fun meal kit brand for millennials and Gen Z" \
  --platform TikTok \
  --tone "casual, witty"
```

View the full setup guide on [GitHub](https://github.com/am-claudia/viral-moment-hijacker-agent#readme).
