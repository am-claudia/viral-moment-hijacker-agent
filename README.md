# Viral Moment Hijacker

An AI marketing agent that monitors what's going viral in any industry, identifies relevant creators, writes personalized outreach, publishes a reactive brand post, and emails your customers — all from a single command.

Built for **Forkly** (a meal kit brand) as a university project on agentic AI systems. Fully general-purpose: swap in any brand, industry, and platform via CLI flags.

---

## What it does

When a trend blows up on TikTok or Instagram, most brands miss the window because the manual workflow is too slow: monitor trends → find creators → research each one → write outreach → draft a post → notify customers. By the time that's done, the moment is stale.

This agent runs that entire workflow autonomously in one pipeline:

```
1. DISCOVER    Scrapes live trending content from your target platform via Apify
               (TikTok scraper, Instagram Hashtag Scraper, or LinkedIn Viral Posts Finder)

2. IDENTIFY    Finds 3 real creators actively posting about the top trend on that platform

3. STRATEGIZE  Picks the brand angle that fits most authentically — flags it if the connection feels forced

4. PERSONALIZE Writes a custom DM pitch for each creator, referencing their specific content and style

5. CREATE      Drafts a reactive brand post in your brand's voice, formatted for the target platform

6. POST        Publishes the brand post to your company's social media account

7. EMAIL       Writes and sends a trend-inspired email to your customer list
               (for meal kit brands: ties the trend to a recipe customers can add to their next delivery)

8. SAVE        Saves the complete campaign package to output/ as a timestamped JSON file
```

A single Claude Opus 4.8 orchestrator runs all reasoning steps. It decides on its own when to call each tool — the same way a human strategist would think through the problem. All creative output (brand angle, DM pitches, brand post, customer email) comes from Claude's own reasoning, not rigid templates.

---

## Project structure

```
viral-moment-hijacker-agent/
├── main.py              CLI entry point — parses args, runs the agent, displays results
├── src/
│   ├── agent.py         Orchestrator — system prompt, agentic loop, tool dispatch logging
│   ├── tools.py         All tool schemas + implementations (trend search, influencer find, post, email, save)
│   └── config.py        Model name + API key loader
├── output/
│   ├── *.json           One campaign file per run
│   └── emails/
│       └── *.txt        Customer email previews
├── .env                 Your API keys (never commit this)
├── .env.example         Template showing which keys are needed
└── requirements.txt     Python dependencies
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

Copy the template:

```bash
cp .env.example .env
```

Then open `.env` and fill in your keys. Instructions for each key are in the next section.

---

## API keys

### Anthropic (required)

The agent is powered by Claude Opus 4.8. Without this key, nothing runs.

1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Sign in → click **API Keys** in the left sidebar → **Create Key**
3. Copy the key (starts with `sk-ant-api03-...`)
4. Paste it in `.env`:

```env
ANTHROPIC_API_KEY=sk-ant-api03-...
```

### Apify (required)

Apify powers both trend discovery and influencer finding. It scrapes live data from TikTok, Instagram, or LinkedIn depending on the platform you choose. The free tier gives $5 in credits — enough for many runs.

1. Go to [apify.com](https://apify.com) and sign up (free)
2. Confirm your email, then log in
3. Click your profile icon (top right) → **Settings** → **Integrations**
4. Under **Personal API tokens**, click **+ Add new token**
5. Name it anything, click **Create**, then copy the token (starts with `apify_api_...`)
6. Paste it into `.env`:

```env
APIFY_API_TOKEN=apify_api_...
```

### Final `.env` file

```env
ANTHROPIC_API_KEY=sk-ant-api03-...
APIFY_API_TOKEN=apify_api_...
```

That's it — two keys and the agent is fully operational.

---

## Running the agent

### Forkly (meal kit brand) on TikTok

```bash
python main.py \
  --industry food \
  --brand-name "Forkly" \
  --brand-description "Fun meal kit brand delivering weekly recipe kits to millennials and Gen Z" \
  --platform TikTok \
  --tone "casual, witty, food-obsessed"
```

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

### B2B startup on LinkedIn

```bash
python main.py \
  --industry fintech \
  --brand-name "PayFlow" \
  --brand-description "B2B payment processing startup" \
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

The terminal shows each step as it executes:

```
VIRAL MOMENT HIJACKER
AI-powered trend + influencer marketing agent

Campaign Configuration
  Brand:    Forkly
  Industry: food
  Platform: TikTok
  Tone:     casual, witty, food-obsessed

── Starting Pipeline ──────────────────────────────────

Claude is reasoning... (step 1)

→ Tool: search_viral_trends
  { "industry": "food", "timeframe": "last 24 hours" }
  ✓ Done   ← scrapes live TikTok data via Apify

→ Tool: find_influencers
  { "trend": "Sourdough Discard Movement", "platform": "TikTok", ... }
  ✓ Done   ← live TikTok scrape, ~30 seconds

Claude is reasoning... (step 3)

→ Tool: post_to_social_media
  { "platform": "TikTok", "post_content": "POV: you saved your sourdough..." }
  ✓ Done

→ Tool: send_customer_email
  { "subject": "Everyone's doing this — and you can cook it 🍜", ... }
  ✓ Done

→ Tool: save_campaign_results
  ✓ Done

── Campaign Complete ───────────────────────────────────

✓ Saved to output/campaign_forkly_20260606_092659.json
```

**Total runtime: 2–4 minutes.** Most of the time is the Apify scraping steps (~30s each) and Claude's reasoning.

---

## Output files

### Campaign JSON — `output/campaign_<brand>_<timestamp>.json`

The complete campaign package:

```json
{
  "metadata": {
    "brand": "Forkly",
    "platform": "TikTok",
    "generated_at": "2026-06-06T09:26:59"
  },
  "viral_trend": "Sourdough Discard / Zero-Waste Cooking Movement",
  "trend_summary": "Eco-conscious food creators are turning sourdough discard into pancakes...",
  "brand_angle": "Extend the 'nothing dies here' energy from the sourdough jar to the whole fridge...",
  "influencer_pitches": [
    {
      "name": "Maya Chen",
      "handle": "@zero_waste_kitchen",
      "followers": "487K",
      "dm_pitch": "Hi Maya! The '1 batch of discard = 24 pancakes' overlay in your latest video..."
    }
  ],
  "brand_post": "POV: you saved your sourdough starter from death but your cilantro has been screaming...",
  "distribution": {
    "social_post_url": "https://www.tiktok.com/@brand/video/abc123xyz",
    "customer_email_subject": "Everyone's doing this — and you can cook it 🍜",
    "customer_email_subscribers": 14230
  }
}
```

### Customer email preview — `output/emails/email_<timestamp>.txt`

The full email Claude wrote for your customer list, saved as plain text.

---

## What's real vs. simulated

| Step | Status | Notes |
|---|---|---|
| Trend discovery | **Real** | Live data scraped from TikTok / Instagram / LinkedIn via Apify |
| Influencer profiles | **Real** | Scraped live via Apify TikTok scraper |
| Claude strategy + DMs + post + email | **Real** | Claude reasons through everything |
| Publishing to your TikTok/Instagram | **Simulated** | Returns a fake post URL; no account needed |
| Sending the customer email | **Simulated** | Saves a preview to `output/emails/`; no email provider needed |

The social posting and email sending are simulated because real publishing APIs (Instagram Graph API, TikTok Business API, Klaviyo, Mailchimp) require business account verification that isn't practical for a demo. In production, you'd swap the function bodies in `src/tools.py` for the real API calls — the rest of the pipeline stays identical.

---

## Architecture

```
main.py  (CLI)
    │
    └── ViralMomentHijacker  (src/agent.py)
            │
            ├── Orchestrator: claude-opus-4-8
            │   adaptive thinking, effort: high
            │   manual agentic loop, max 15 iterations
            │
            └── Tools  (src/tools.py)
                    ├── search_viral_trends()     Apify — platform-specific trend scraper
                    │                             TikTok → clockworks/tiktok-scraper
                    │                             Instagram → apify/instagram-hashtag-scraper
                    │                             LinkedIn → scarletapi/linkedin-viral-posts-finder
                    ├── find_influencers()         Apify — clockworks/tiktok-scraper
                    ├── post_to_social_media()     Platform publishing API (simulated)
                    ├── send_customer_email()      Email provider API (simulated)
                    └── save_campaign_results()    Writes output JSON
```

**Why claude-opus-4-8 with adaptive thinking?**
The campaign strategy requires multi-step reasoning: evaluating trend fit, picking a brand angle, personalizing three separate DM pitches, and writing both a platform post and a customer email in the same voice. Adaptive thinking lets Claude decide how deeply to reason about each step rather than using a fixed compute budget.

**Why a manual agentic loop?**
The manual loop in `agent.py` gives full control to log each tool call in the terminal, inject the brand name into the save tool, and track intermediate results (post URL, email stats) for the final display. The Anthropic tool runner would work too but hides intermediate steps.

**Why simulated posting and email?**
Real social publishing and email APIs require business accounts, domain verification, and OAuth flows that complicate a demo. The simulated tools generate realistic output (fake post URL, subscriber count, open rate estimate) so the full pipeline can run end-to-end without external accounts.

---

## Troubleshooting

**`APIFY_API_TOKEN not set`**
Add your Apify token to `.env`. See the API keys section above.

**`ModuleNotFoundError`**
Run `pip install -r requirements.txt` — you likely skipped the install step.

**Agent stops mid-run with a billing error**
Check your Anthropic account balance at [console.anthropic.com](https://console.anthropic.com). Claude Opus 4.8 costs roughly $0.05–0.15 per full campaign run.

**Apify run hangs for more than 2 minutes**
Apify occasionally has slow cold starts. Cancel and re-run — the second attempt is usually fast.
