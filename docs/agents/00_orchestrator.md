# Orchestrator — ViralMomentHijacker

## Overview

| Property | Value |
|---|---|
| **File** | `src/agent.py` |
| **Class** | `ViralMomentHijacker` |
| **Model** | `claude-opus-4-8` with adaptive thinking |
| **Thinking** | `{"type": "adaptive"}` + `output_config: {"effort": "high"}` |
| **Max iterations** | 15 |

---

## Role

The Orchestrator is the brain of the pipeline. It coordinates all sub-agents and tools, reasons about strategy, and produces the creative content (DM pitches, brand post, hashtags, calendar) itself.

It does **not** do data collection or email writing — those are delegated to specialized sub-agents.

---

## What the Orchestrator Does Directly

| Task | How |
|---|---|
| Choose brand angle | Pure reasoning (no tool) |
| Write DM pitches | Pure reasoning, using InfluencerAgent's scored profiles |
| Write brand post | Pure reasoning |
| Write hashtag groups | Calls `generate_hashtag_strategy` (formats its own output) |
| Write content calendar | Calls `generate_content_calendar` (formats its own output) |

## What the Orchestrator Delegates

| Task | Sub-agent / Tool |
|---|---|
| Find viral trends | `TrendResearchAgent` via `search_viral_trends` |
| Score influencers | `InfluencerAgent` via `find_influencers` |
| Write & send email | `EmailAgent` via `send_customer_email` |
| Publish social post | `post_to_social_media` (simulated) |
| Save all results | `save_campaign_results` (Python function) |

---

## Agentic Loop

```python
for iteration in range(MAX_ITERATIONS):          # max 15 turns
    response = client.messages.create(...)        # call Opus

    if response.stop_reason == "end_turn":
        break                                     # Claude is done

    if response.stop_reason == "tool_use":
        for block in response.content:            # execute each tool
            result = execute_tool(block.name, block.input, ...)
            tool_results.append(result)

        messages.append(tool_results)             # feed results back
```

The loop runs until Claude stops calling tools (`end_turn`) or the 15-iteration safety cap is hit.

---

## System Prompt Structure

The Orchestrator's system prompt (built in `_system_prompt()`) contains:

1. **Brand context** — name, description, tone, values
2. **Sub-agent directory** — what each sub-agent does and when to call it
3. **10-step mission** — the exact pipeline steps in order
4. **Quality rules** — DM tone, platform format conventions, authenticity over virality

---

## Why Opus with Adaptive Thinking?

The Orchestrator handles tasks that require multi-step reasoning in a single response:
- Evaluating 3 trends and picking the most authentic angle
- Writing 3 distinct DM pitches for different creator personalities
- Producing a 7-day campaign arc with platform-specific formats

Adaptive thinking lets Opus decide how much to reason per step — heavier on strategy, lighter on formatting. `effort: "high"` keeps quality consistent throughout the full pipeline.

---

## Tools Available

| Tool | What it calls |
|---|---|
| `search_viral_trends` | TrendResearchAgent |
| `find_influencers` | InfluencerAgent |
| `send_customer_email` | EmailAgent |
| `post_to_social_media` | Simulated function |
| `generate_hashtag_strategy` | Pass-through formatter |
| `generate_content_calendar` | Pass-through formatter |
| `save_campaign_results` | Persistence function |
