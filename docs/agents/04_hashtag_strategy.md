# Task 4 — HASHTAGS: Generate Hashtag Strategy

## Agent: Orchestrator (ViralMomentHijacker) + Formatter Tool

| Property | Value |
|---|---|
| **File** | `src/tools.py` → `generate_hashtag_strategy()` |
| **Model** | `gemini-2.5-pro` (writes the hashtags) |
| **Triggered by** | `generate_hashtag_strategy` tool call from the Orchestrator |
| **Type** | Pass-through formatter (no sub-agent) |

---

## What It Does

The Orchestrator writes all hashtag groups itself — this is a creative task that benefits from its full context about the brand, platform, and chosen trend. The tool simply **validates the structure and returns it** in a consistent format ready for the final campaign save.

No additional Gemini call is made here. The tool is a formatter, not a reasoner.

---

## Inputs

The Orchestrator calls `generate_hashtag_strategy` with four groups it has written:

```json
{
  "broad": ["#food", "#mealprep", "#cooking", "#easyrecipes"],
  "niche": ["#mealkit", "#quickdinner", "#gymfood", "#fitnessmeal"],
  "branded": ["#Forkly", "#ForklyFresh"],
  "trend": ["#gymstreak", "#25daystreak", "#streaklife", "#gymfood"],
  "caption_formula": "Open with 1 broad + 2 niche tags, close with trend + branded tags"
}
```

### Group Definitions

| Group | Size | Volume target |
|---|---|---|
| `broad` | 3–5 tags | 1M+ posts — for reach |
| `niche` | 4–6 tags | 10K–500K posts — for targeted engagement |
| `branded` | 1–2 tags | Brand-owned — for community building |
| `trend` | 3–5 tags | Trend-specific — to ride the moment |

---

## Outputs

The tool returns a formatted JSON object and the Orchestrator passes it to `save_campaign_results` at the end:

```json
{
  "success": true,
  "groups": {
    "broad": ["#food", "#mealprep", "#cooking", "#easyrecipes"],
    "niche": ["#mealkit", "#quickdinner", "#gymfood", "#fitnessmeal"],
    "branded": ["#Forkly", "#ForklyFresh"],
    "trend": ["#gymstreak", "#25daystreak", "#streaklife", "#gymfood"]
  },
  "caption_formula": "Open with 1 broad + 2 niche tags, close with trend + branded tags",
  "full_set": "#food #mealprep #cooking ... #gymstreak",
  "total_tags": 15
}
```

A separate `output/hashtags/hashtags_<brand>_<timestamp>.txt` file is also written when `save_campaign_results` runs.

---

## Why This Design

- **Orchestrator writes, tool formats**: Hashtag selection requires knowing the brand, the trend, and the platform convention. The Orchestrator has all of this — no need for a sub-agent.
- **No sub-agent**: A dedicated hashtag sub-agent would add a Gemini API call for a task the Orchestrator already does well. Pass-through tools are lighter and faster.
- **Saved separately**: The hashtag file in `output/hashtags/` makes it easy to copy-paste without opening the full campaign JSON.
