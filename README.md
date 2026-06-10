# Viral Moment Hijacker

An AI agent that monitors what's going viral in any industry, identifies the right creators to partner with, writes personalized outreach, publishes a reactive brand post, and emails your customers — all from a single command.

---

## The problem it solves

When a trend blows up, the brands that win are the ones that respond within hours — not days. But the manual workflow is too slow: monitor platforms → find relevant creators → research each one → write personalized outreach → draft a post → notify your customers. By the time all of that is done, the moment has passed and the audience has moved on.

This agent runs that entire workflow in one automated pipeline. It scrapes live trend data, evaluates real creator profiles, reasons about the right brand angle, and produces ready-to-use content — all driven by a Claude Opus orchestrator that makes strategic decisions the same way a human strategist would.

**For marketers, this means:**
- Catching viral moments in the same news cycle they happen
- Getting a full campaign (influencer outreach + brand post + customer email + 7-day content calendar) in under 5 minutes
- Personalized DM pitches that reference each creator's actual content — not generic templates
- A documented strategy with brand angle reasoning, not just generated copy

---

## How it works

```
1. DISCOVER    Scrapes live trending content from your target platform via Apify
               TikTok, Instagram, or LinkedIn — real posts, real engagement numbers

2. ANALYZE     TrendResearchAgent ranks the scraped data by opportunity score
               and returns content angles, not just raw hashtags

3. IDENTIFY    InfluencerAgent evaluates real creator profiles for niche fit
               Returns scored matches with a "why good fit" explanation per creator

4. STRATEGIZE  Orchestrator picks the brand angle that fits most authentically
               Flags it if the connection feels forced — won't produce dishonest copy

5. HASHTAGS    Generates a grouped strategy: broad reach + niche + branded + trend-specific
               Includes a caption formula showing how to mix the groups per post

6. PERSONALIZE Writes a custom DM pitch per creator using their content style,
               engagement pattern, and most recent trend-related post

7. CREATE      Drafts a reactive brand post in your brand's voice,
               formatted for the target platform's native style

8. CALENDAR    Produces a 7-day content plan: day 1 jumps on the trend,
               days 2–5 sustain it, days 6–7 convert with a CTA

9. POST        Publishes the brand post to your social media account

10. EMAIL      EmailAgent writes a full customer email connecting the trend to
               a specific product recommendation, then sends it to your list

11. SAVE       Writes the complete campaign package to output/ as a timestamped JSON
```

---

## Multi-agent architecture

The agent is built as an orchestrator that coordinates three specialized sub-agents. Each sub-agent is its own Claude API call with a focused system prompt and the right model for its job.

```
Claude Opus 4.8 (Orchestrator)
    Handles: strategy, brand angle, DM pitches, brand post, content calendar
    │
    ├── search_viral_trends  →  TrendResearchAgent  (claude-haiku-4-5)
    │                           Scrapes Apify live data, then analyzes and ranks
    │                           trends by opportunity score + suggests content angles
    │
    ├── find_influencers     →  InfluencerAgent     (claude-haiku-4-5)
    │                           Scrapes Apify creator profiles, scores each on
    │                           niche fit, returns ranked matches with why_good_fit
    │
    └── send_customer_email  →  EmailAgent          (claude-sonnet-4-6)
                                Writes the full email (subject, body, CTA)
                                from trend context, then simulates sending
```

The orchestrator never writes the email itself — it delegates to the EmailAgent with just the trend name, trend summary, and brand angle. The EmailAgent handles all copywriting. Same pattern for trends and influencers: the orchestrator receives analyzed reports, not raw scraped data, so it can focus on strategy.

**Why this matters:** Each agent has one job and the right model for it. Haiku is fast and cheap for structured data analysis. Sonnet produces better creative copy. Opus handles the multi-step strategic reasoning that ties everything together.

---

## Project structure

```
viral-moment-hijacker-agent/
├── main.py                  CLI entry point
├── src/
│   ├── agent.py             Orchestrator — system prompt, agentic loop, tool dispatch
│   ├── tools.py             Tool schemas + dispatcher (delegates to sub-agents)
│   ├── config.py            Model constants for orchestrator + all 3 sub-agents
│   └── agents/
│       ├── trend_agent.py       TrendResearchAgent — scrape + analyze trends
│       ├── influencer_agent.py  InfluencerAgent — scrape + score creators
│       └── email_agent.py       EmailAgent — write + send customer email
├── output/
│   ├── campaigns/           Full campaign JSON, one file per run
│   ├── calendars/           7-day content calendar as plain text
│   ├── hashtags/            Hashtag strategy as plain text
│   └── emails/              Customer email previews as plain text
├── .env                     Your API keys (never commit this)
├── .env.example             Template showing which keys are needed
└── requirements.txt         Python dependencies
```

---

## Setup

### 1. Check Python version

You need Python 3.11 or higher.

```bash
python --version
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

This installs: `anthropic`, `python-dotenv`, `rich`, `apify-client`.

### 3. Create your `.env` file

```bash
cp .env.example .env
```

Then open `.env` and fill in your keys. Instructions for each key are in the next section.

---

## API keys

### Anthropic (required)

Powers all Claude models in the pipeline (Opus, Sonnet, Haiku).

1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Sign in → **API Keys** in the left sidebar → **Create Key**
3. Copy the key (starts with `sk-ant-api03-...`)
4. Paste it in `.env`:

```env
ANTHROPIC_API_KEY=sk-ant-api03-...
```

### Apify (required)

Powers live social media scraping for both trend discovery and influencer finding. The free tier gives $5 in credits — enough for many runs.

1. Go to [apify.com](https://apify.com) and sign up (free)
2. Confirm your email, then log in
3. Click your profile icon (top right) → **Settings** → **Integrations**
4. Under **Personal API tokens**, click **+ Add new token**
5. Name it anything, click **Create**, then copy the token (starts with `apify_api_...`)
6. Paste it in `.env`:

```env
APIFY_API_TOKEN=apify_api_...
```

### Final `.env` file

```env
ANTHROPIC_API_KEY=sk-ant-api03-...
APIFY_API_TOKEN=apify_api_...
```

---

## Running the agent

### Fitness brand on Instagram

```bash
python main.py \
  --industry fitness \
  --brand-name "ActiveWear Co" \
  --brand-description "Sustainable activewear for everyday athletes" \
  --platform Instagram \
  --tone casual \
  --brand-values "sustainability, performance, community"
```

### Food brand on TikTok

```bash
python main.py \
  --industry food \
  --brand-name "YourBrand" \
  --brand-description "One sentence describing what your brand does and who it's for" \
  --platform TikTok \
  --tone "casual, witty, food-obsessed"
```

### B2B startup on LinkedIn

```bash
python main.py \
  --industry fintech \
  --brand-name "PayFlow" \
  --brand-description "B2B payment processing startup for fast-growing companies" \
  --platform LinkedIn \
  --tone professional \
  --brand-values "transparent, founder-friendly, no hidden fees"
```

### All CLI flags

| Flag | Required | Description |
|---|---|---|
| `--industry` | Yes | Industry to monitor (e.g. `food`, `fitness`, `beauty`, `fintech`) |
| `--brand-name` | Yes | Your brand name |
| `--brand-description` | Yes | One sentence describing the brand |
| `--platform` | Yes | `TikTok`, `Instagram`, or `LinkedIn` |
| `--tone` | No | Brand voice, default: `casual` |
| `--brand-values` | No | Comma-separated values, default: `authentic, creative, community-driven` |

---

## What to expect when it runs

The terminal shows each step as it executes, including which sub-agent is running:

```
╭─────────────────────────────────────────────╮
│           VIRAL MOMENT HIJACKER             │
│  AI-powered trend + influencer marketing    │
╰─────────────────────────────────────────────╯

Campaign Configuration
  Brand:    ActiveWear Co
  Industry: fitness
  Platform: Instagram
  Tone:     casual

── Starting Pipeline ──────────────────────────────────

Claude is reasoning... (step 1)

→ Tool: search_viral_trends
  { "industry": "fitness", "timeframe": "last 24 hours" }
  Executing search_viral_trends...     ← TrendResearchAgent scrapes Apify + analyzes
  ✓ Done

→ Tool: find_influencers
  { "trend": "25-Day Gym Streak", "platform": "Instagram", ... }
  Executing find_influencers...        ← InfluencerAgent scrapes + scores creators
  ✓ Done

Claude is reasoning... (step 3)        ← Orchestrator picks brand angle + writes DMs + post

→ Tool: generate_hashtag_strategy
  ✓ Done

→ Tool: generate_content_calendar
  ✓ Done

→ Tool: post_to_social_media
  ✓ Done

→ Tool: send_customer_email
  { "trend_name": "25-Day Gym Streak", ... }
  Executing send_customer_email...     ← EmailAgent writes the email
  ✓ Done

→ Tool: save_campaign_results
  ✓ Done

── Campaign Complete ───────────────────────────────────

✓ Saved to output/campaigns/campaign_activewear_co_20260610_142301.json
```

**Total runtime: 2–5 minutes.** Most of the time is Apify scraping (~30–60s per step).

---

## Output files

### `output/campaigns/campaign_<brand>_<timestamp>.json`

The complete campaign package:

```json
{
  "metadata": {
    "brand": "ActiveWear Co",
    "platform": "Instagram",
    "generated_at": "2026-06-10T14:23:01"
  },
  "viral_trend": "25-Day Gym Streak Challenge",
  "trend_summary": "Fitness creators are documenting unbroken 25-day gym streaks...",
  "brand_angle": "Be the brand that makes the streak physically sustainable — not just mentally...",
  "influencer_pitches": [
    {
      "name": "Jordan Lee",
      "handle": "@jordanlifts",
      "followers": "210K",
      "dm_pitch": "Hey Jordan! The progression shots in your Day 18 reel are exactly the kind of content..."
    }
  ],
  "brand_post": "Day 25 looks different in every body. Same gear. 🌱 #GymStreak #ActiveWearCo",
  "distribution": {
    "social_post_url": "https://www.instagram.com/p/abc123/",
    "customer_email_subject": "Your streak deserves gear that keeps up",
    "customer_email_subscribers": 18400
  },
  "content_calendar": [...],
  "hashtag_strategy": { "groups": { "broad": [...], "niche": [...], "branded": [...], "trend": [...] } }
}
```

### `output/calendars/calendar_<brand>_<timestamp>.txt`

The 7-day posting plan as readable plain text.

### `output/hashtags/hashtags_<brand>_<timestamp>.txt`

All hashtag groups and the caption formula.

### `output/emails/email_<timestamp>.txt`

The full customer email the EmailAgent wrote, saved as plain text.

---

## What's real vs. simulated

| Step | Status | Notes |
|---|---|---|
| Trend discovery | **Real** | Live data scraped from TikTok / Instagram / LinkedIn via Apify |
| Influencer profiles | **Real** | Scraped live — real follower counts, bios, recent posts |
| Strategy, DMs, brand post | **Real** | Claude Opus reasons through all of it |
| Customer email | **Real** | EmailAgent writes original copy from your brand context |
| Publishing to social media | **Simulated** | Returns a fake post URL; no platform account needed |
| Sending the customer email | **Simulated** | Saves a preview to `output/emails/`; no email provider needed |

Publishing and email sending are simulated because real APIs (Instagram Graph API, TikTok Business API, Klaviyo, Mailchimp) require business accounts and OAuth verification that aren't practical for a demo environment. In production, you'd replace the simulation blocks in `src/tools.py` and `src/agents/email_agent.py` with real API calls — the rest of the pipeline stays identical.

---

## Troubleshooting

**`APIFY_API_TOKEN not set`**  
Add your Apify token to `.env`. See the API keys section above.

**`ModuleNotFoundError`**  
Run `pip install -r requirements.txt`.

**Agent stops mid-run with a billing error**  
Check your Anthropic account balance at [console.anthropic.com](https://console.anthropic.com). A full campaign run uses Opus (orchestrator), Sonnet (email), and Haiku (trends + influencers) — typically $0.05–0.20 total.

**Apify run hangs for more than 2 minutes**  
Apify occasionally has slow cold starts. Cancel and re-run — the second attempt is usually fast.

**`json.JSONDecodeError` from a sub-agent**  
A sub-agent occasionally returns non-JSON text if Claude prefixes its response. The EmailAgent has a fallback that surfaces the raw response. Re-running usually resolves it.
