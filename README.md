# Viral Moment Hijacker

An AI agent that monitors what's going viral in any industry, identifies the right creators to partner with, writes personalized outreach, and emails your customers — all from a single command.

---

## The problem it solves

When a trend blows up, the brands that win are the ones that respond within hours — not days. But the manual workflow is too slow: monitor platforms → find relevant creators → research each one → write personalized outreach → draft a post → notify your customers. By the time all of that is done, the moment has passed and the audience has moved on.

This agent runs that entire workflow in one automated pipeline. It scrapes live trend data, evaluates real creator profiles, reasons about the right brand angle, and produces ready-to-use content — all driven by a Gemini Flash orchestrator that makes strategic decisions the same way a human strategist would.

**For marketers, this means:**
- Catching viral moments in the same news cycle they happen
- Getting a full campaign (brand angle + DM pitches + customer email) in under 5 minutes
- Personalized DM pitches that reference each creator's actual content — not generic templates
- A documented strategy with brand angle reasoning, not just generated copy

---

## How it works

The pipeline has a core that always runs, plus two optional agents you enable with flags:

```
Core (always active)
──────────────────────────────────────────────────────────
1. DISCOVER    Scrapes live trending content from your target platform via Apify
               TikTok, Instagram, or LinkedIn — real posts, real engagement numbers

2. STRATEGIZE  Orchestrator picks the brand angle that fits most authentically
               Flags it if the connection feels forced — won't produce dishonest copy

3. SAVE        Writes the complete campaign package to output/ as a timestamped JSON

With --find-influencers
──────────────────────────────────────────────────────────
4. IDENTIFY    InfluencerAgent evaluates real creator profiles for niche fit
               Returns scored matches with a "why good fit" explanation per creator

5. PERSONALIZE Writes a custom DM pitch per creator using their content style,
               engagement pattern, and most recent trend-related post

With --send-email
──────────────────────────────────────────────────────────
6. EMAIL       EmailAgent writes a full customer email connecting the trend to
               a specific product recommendation, then sends it to your list
```

---

## Multi-agent architecture

The agent is built as an orchestrator that coordinates up to two specialized sub-agents. Each sub-agent is its own Gemini API call with a focused system prompt. Only the agents enabled by CLI flags are wired into the pipeline.

```
gemini-2.5-flash (Orchestrator)
    Handles: strategy, brand angle, DM pitches
    │
    ├── search_viral_trends  →  TrendResearchAgent  (gemini-2.5-flash)
    │                           Always active. Scrapes Apify live data, then analyzes
    │                           and ranks trends by opportunity score + content angles.
    │
    ├── find_influencers     →  InfluencerAgent     (gemini-2.5-flash)   [--find-influencers]
    │                           Scrapes Apify creator profiles, scores each on
    │                           niche fit, returns ranked matches with why_good_fit.
    │
    └── send_customer_email  →  EmailAgent          (gemini-2.5-flash)   [--send-email]
                                Writes the full email (subject, body, CTA)
                                from trend context, then simulates sending.
```

**How the orchestrator's tools are built dynamically:** `_build_tools()` in `src/agent.py` only exposes tools for enabled agents. Without `--find-influencers`, the orchestrator never receives `find_influencers` as an available function, so it focuses entirely on trend strategy and brand angle. The system prompt is also generated dynamically — numbered steps only include the active agents.

**Why this matters:** Each agent has one focused job and the right model for it. Flash handles everything — it's fast, cheap, and capable enough for structured data analysis, creative writing, and multi-step strategy all in one.

---

## Project structure

```
viral-moment-hijacker-agent/
├── main.py                  CLI entry point
├── src/
│   ├── agent.py             Orchestrator — system prompt, agentic loop, tool dispatch
│   ├── tools.py             Tool schemas + dispatcher (delegates to sub-agents)
│   ├── config.py            Model constants for orchestrator + all sub-agents
│   └── agents/
│       ├── trend_agent.py       TrendResearchAgent — scrape + analyze trends
│       ├── influencer_agent.py  InfluencerAgent — scrape + score creators
│       └── email_agent.py       EmailAgent — write + send customer email
├── output/
│   ├── campaigns/           Full campaign JSON, one file per run
│   ├── calendars/           7-day content calendar as plain text (if generated)
│   ├── hashtags/            Hashtag strategy as plain text (if generated)
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

This installs: `google-genai`, `python-dotenv`, `rich`, `apify-client`.

### 3. Create your `.env` file

```bash
cp .env.example .env
```

Then open `.env` and fill in your keys. Instructions for each key are in the next section.

---

## API keys

### Google Gemini (required)

Powers all Gemini models in the pipeline (gemini-2.5-flash throughout).

1. Go to [aistudio.google.com](https://aistudio.google.com)
2. Sign in → click **Get API key** → **Create API key**
3. Copy the key (starts with `AIza...`)
4. Paste it in `.env`:

```env
GEMINI_API_KEY=AIza...
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
GEMINI_API_KEY=AIza...
APIFY_API_TOKEN=apify_api_...
```

---

## Running the agent

### Core pipeline only — trend + brand angle

```bash
python main.py \
  --industry fitness \
  --brand-name "ActiveWear Co" \
  --brand-description "Sustainable activewear for everyday athletes" \
  --platform Instagram \
  --tone casual
```

### Add influencer outreach

```bash
python main.py \
  --industry food \
  --brand-name "Forkly" \
  --brand-description "Fun meal kit brand delivering weekly recipe kits to millennials and Gen Z" \
  --platform TikTok \
  --tone "casual, witty, food-obsessed" \
  --find-influencers
```

### Full pipeline — trends + influencers + customer email

```bash
python main.py \
  --industry fintech \
  --brand-name "PayFlow" \
  --brand-description "B2B payment processing startup for fast-growing companies" \
  --platform LinkedIn \
  --tone professional \
  --brand-values "transparent, founder-friendly, no hidden fees" \
  --find-influencers \
  --send-email
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
| `--find-influencers` | No | Enable InfluencerAgent: find and score creators, then write personalized DM pitches |
| `--send-email` | No | Enable EmailAgent: write and send a trend-inspired customer email |

---

## What to expect when it runs

The terminal shows each step as it executes, including which sub-agents are active:

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
  Agents:   TrendResearchAgent, InfluencerAgent, EmailAgent

── Starting Pipeline ──────────────────────────────────

Gemini is reasoning... (step 1)

→ Tool: search_viral_trends
  { "industry": "fitness", "timeframe": "last 24 hours" }
  Executing search_viral_trends...     ← TrendResearchAgent scrapes Apify + analyzes
  ✓ Done

→ Tool: find_influencers
  { "trend": "25-Day Gym Streak", "platform": "Instagram", ... }
  Executing find_influencers...        ← InfluencerAgent scrapes + scores creators
  ✓ Done

Gemini is reasoning... (step 3)        ← Orchestrator picks brand angle + writes DM pitches

→ Tool: send_customer_email
  { "trend_name": "25-Day Gym Streak", ... }
  Executing send_customer_email...     ← EmailAgent writes the email
  ✓ Done

→ Tool: save_campaign_results
  ✓ Done

── Campaign Complete ───────────────────────────────────

✓ Saved to output/campaigns/campaign_activewear_co_20260610_142301.json

╭─ Campaign Summary ──────────────────────────────────╮
│ 25-Day Gym Streak Challenge                         │
│                                                     │
│ Brand angle: Be the brand that makes the streak     │
│ physically sustainable — not just mentally...       │
╰─────────────────────────────────────────────────────╯

✓ 3 influencer DM pitch(es) generated

╭─ DM Pitch — Jordan Lee ─────────────────────────────╮
│ @jordanlifts  ·  210K followers                     │
│                                                     │
│ Hey Jordan! The progression shots in your Day 18    │
│ reel are exactly the kind of content...             │
╰─────────────────────────────────────────────────────╯

Distribution
  ✓ Email sent to 18,400 subscribers: "Your streak deserves gear that keeps up"
```

The `Agents:` line in Campaign Configuration shows which agents are active for this run.

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
    "social_post_url": null,
    "customer_email_subject": "Your streak deserves gear that keeps up",
    "customer_email_subscribers": 18400
  },
  "content_calendar": [],
  "hashtag_strategy": {}
}
```

`influencer_pitches` and `distribution.customer_email_*` are only populated when `--find-influencers` and `--send-email` are passed, respectively.

### `output/emails/email_<timestamp>.txt`

The full customer email the EmailAgent wrote, saved as plain text. Only created when `--send-email` is active.

---

## Standalone agent testing

Each sub-agent can be run directly for testing without going through the full pipeline:

```bash
# Test TrendResearchAgent
python -m src.agents.trend_agent \
  --industry fitness \
  --platform Instagram \
  --timeframe "last 24 hours"

# Test InfluencerAgent
python -m src.agents.influencer_agent \
  --trend "#gymstreak" \
  --platform TikTok \
  --niche "fitness motivation" \
  --count 3

# Test EmailAgent
python -m src.agents.email_agent \
  --trend-name "25-Day Gym Streak" \
  --trend-summary "Fitness creators documenting unbroken 25-day streaks..." \
  --brand-angle "Be the gear that makes the streak sustainable" \
  --brand-name "ActiveWear Co" \
  --brand-description "Sustainable activewear for everyday athletes" \
  --tone casual
```

---

## What's real vs. simulated

| Step | Status | Notes |
|---|---|---|
| Trend discovery | **Real** | Live data scraped from TikTok / Instagram / LinkedIn via Apify |
| Influencer profiles | **Real** | Scraped live — real follower counts, bios, recent posts |
| Strategy, DMs, brand angle | **Real** | Gemini Flash reasons through all of it |
| Customer email | **Real** | EmailAgent writes original copy from your brand context |
| Sending the customer email | **Simulated** | Saves a preview to `output/emails/`; no email provider needed |

Email sending is simulated because real APIs (Klaviyo, Mailchimp, SendGrid) require business accounts and API setup that aren't practical for a demo. In production, replace the simulation block in `src/agents/email_agent.py` with a real API call — the email content is already written by the agent, just pass it to the provider.

---

## Troubleshooting

**`GEMINI_API_KEY not set`**  
Add your Gemini API key to `.env`. See the API keys section above.

**`APIFY_API_TOKEN not set`**  
Add your Apify token to `.env`. See the API keys section above.

**`ModuleNotFoundError`**  
Run `pip install -r requirements.txt`.

**Agent stops mid-run with a billing error**  
Check your Google AI Studio quota at [aistudio.google.com](https://aistudio.google.com). A full campaign run uses gemini-2.5-flash for all steps.

**Apify run hangs for more than 2 minutes**  
Apify occasionally has slow cold starts. Cancel and re-run — the second attempt is usually fast.

**`json.JSONDecodeError` from a sub-agent**  
A sub-agent occasionally returns non-JSON text if Gemini prefixes its response. The EmailAgent has a fallback that surfaces the raw response. Re-running usually resolves it.
