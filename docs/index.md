---
title: Viral Moment Hijacker
layout: home
---

# Viral Moment Hijacker

An AI agent that monitors what's going viral in any industry, identifies the right creators to partner with, writes personalized outreach, publishes a reactive brand post, and emails your customers — all from a single command.

---

## The problem it solves

When a trend blows up, the brands that win are the ones that respond within hours — not days. The manual workflow is too slow: monitor platforms → find relevant creators → research each one → write personalized outreach → draft a post → notify your customers. By the time all of that is done, the moment has passed.

This agent runs that entire workflow in one automated pipeline.

---

## How it works

| Step | Task | Agent |
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

## Multi-agent architecture

```
Claude Opus 4.8 (Orchestrator)
    │
    ├── search_viral_trends  →  TrendResearchAgent  (claude-haiku-4-5)
    ├── find_influencers     →  InfluencerAgent     (claude-haiku-4-5)
    └── send_customer_email  →  EmailAgent          (claude-sonnet-4-6)
```

Each sub-agent is its own Claude API call with a focused system prompt and the right model for its job. The orchestrator receives pre-analyzed reports — not raw data — so it can focus entirely on strategy.

---

## Agent docs

- [Orchestrator](agents/00_orchestrator.md)
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

Full setup instructions in the [README](https://github.com/am-claudia/viral-moment-hijacker-agent#readme).
