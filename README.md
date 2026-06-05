# Viral Moment Hijacker

## About

Viral Moment Hijacker is an AI-powered marketing agent that helps brands jump on trending cultural moments before the window closes. Instead of spending hours manually monitoring social media, researching creators, and drafting outreach copy, this agent does it all in a single automated pipeline — in under a minute.

The agent was built for **Forkly**, a fictional meal kit brand targeting millennials and Gen Z, as a university project exploring agentic AI systems with tool use. It is designed to be general-purpose: you can point it at any brand, industry, and platform by passing your brand config through the CLI.

### The problem it solves

When something goes viral on TikTok or Instagram, brands have a narrow window to respond authentically before the moment is stale. Most marketing teams miss it because the process is too slow: monitor trends → identify relevant creators → research each one → draft outreach → write a reactive post. By the time that's done, the trend has peaked.

This agent compresses that entire workflow into one command.

### How it works at a high level

A single Claude Opus 4.8 orchestrator runs as an autonomous agent with access to three tools. It decides on its own when to search for trends, when to look up influencers, and when to save the results — the same way a human strategist would work through the problem step by step. All the creative work (picking the brand angle, writing DMs, drafting the post) happens through Claude's own reasoning, not rigid templates.

AI marketing agent that hijacks viral moments for any brand — finds trending topics, discovers relevant influencers, writes personalized DM pitches, and generates a reactive brand post in one automated pipeline.

## Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Add your API key
cp .env.example .env
# Edit .env and paste your ANTHROPIC_API_KEY from console.anthropic.com
```

## Usage

```bash
# Forkly on TikTok
python main.py \
  --industry food \
  --brand-name "Forkly" \
  --brand-description "Fun meal kit brand delivering weekly recipe kits to millennials and Gen Z" \
  --platform TikTok \
  --tone "casual, witty, food-obsessed"

# Any brand on Instagram
python main.py \
  --industry fitness \
  --brand-name "ActiveWear Co" \
  --brand-description "Sustainable activewear for everyday athletes" \
  --platform Instagram \
  --tone casual \
  --brand-values "sustainability, performance, community"

# B2B on LinkedIn
python main.py \
  --industry fintech \
  --brand-name "PayFlow" \
  --brand-description "B2B payment processing startup" \
  --platform LinkedIn \
  --tone professional
```

## What it does

```
1. DISCOVER   search_viral_trends(industry, timeframe)
               → returns ranked trending topics with sentiment + opportunity data

2. IDENTIFY   find_influencers(trend, platform, niche)
               → returns creator profiles: followers, engagement, recent content

3. STRATEGIZE  Claude reasoning
               → picks the most authentic brand angle, flags forced ones

4. PERSONALIZE Claude reasoning
               → writes platform-native DM pitches referencing each creator's actual content

5. CREATE      Claude reasoning
               → generates a reactive brand post in the brand's voice

6. SAVE        save_campaign_results(campaign_data)
               → writes full campaign package to output/<brand>_<timestamp>.json
```

## Output

Each run saves a JSON file to `output/`:

```json
{
  "metadata": { "brand": "Forkly", "platform": "TikTok", "generated_at": "..." },
  "viral_trend": "Cucumber Salad ASMR",
  "trend_summary": "...",
  "brand_angle": "...",
  "influencer_pitches": [
    { "name": "...", "handle": "@...", "followers": "245K", "dm_pitch": "..." }
  ],
  "brand_post": "..."
}
```

## Architecture

- **Orchestrator**: `claude-opus-4-8` with adaptive thinking + `effort: high`
- **Data tools**: `claude-haiku-4-5` for realistic mock trend and influencer data
- **Loop**: manual agentic loop in `src/agent.py` — Claude decides when to call each tool
