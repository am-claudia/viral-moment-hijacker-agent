# Task 7 — CALENDAR: Generate Content Calendar

## Agent: Orchestrator (ViralMomentHijacker) + Formatter Tool

| Property | Value |
|---|---|
| **File** | `src/tools.py` → `generate_content_calendar()` |
| **Model** | `claude-opus-4-8` (writes the calendar) |
| **Triggered by** | `generate_content_calendar` tool call from the Orchestrator |
| **Type** | Pass-through formatter (no sub-agent) |

---

## What It Does

The Orchestrator writes a full 7-day content plan and calls `generate_content_calendar` to validate and store it. Like the hashtag strategy, the tool is a **formatter** — it structures and returns the data the Orchestrator already produced.

The 7-day arc follows a deliberate narrative structure:
- **Day 1**: Jump on the trend while it's hot
- **Days 2–5**: Sustain with related content that deepens the brand angle
- **Days 6–7**: Convert with a clear CTA (shop, sign up, try a kit)

---

## Inputs

The Orchestrator calls `generate_content_calendar` with exactly 7 day objects:

```json
{
  "days": [
    {
      "day": "Monday",
      "format": "Reel",
      "caption": "25 days of the gym streak challenge just hit different when your meals are already handled. 🔥 #gymstreak #Forkly",
      "optimal_time": "7:00 PM"
    },
    {
      "day": "Tuesday",
      "format": "Story",
      "caption": "Behind the scenes: how we build a week of meals around your streak goals",
      "optimal_time": "12:00 PM"
    }
  ]
}
```

### Platform-Native Formats

The Orchestrator is instructed to only use formats native to the target platform:

| Platform | Allowed Formats |
|---|---|
| TikTok | Video, Duet, Stitch, Carousel, Story |
| Instagram | Reel, Story, Carousel, Feed Post |
| LinkedIn | Post, Article, Video |

---

## Outputs

The tool returns a structured object:

```json
{
  "success": true,
  "days_planned": 7,
  "calendar": [ ... 7 day objects ... ]
}
```

The Orchestrator stores this and passes `calendar` to `save_campaign_results` at the end. A separate `output/calendars/calendar_<brand>_<timestamp>.txt` file is also written for easy reading.

### Calendar TXT format (saved at the end):
```
7-DAY CONTENT CALENDAR
==================================================

📅 MONDAY
   Format : Reel
   Time   : 7:00 PM
   Caption: 25 days of the gym streak challenge just hit different...

📅 TUESDAY
   ...
```

---

## Why This Design

- **Orchestrator writes, tool formats**: A 7-day narrative arc requires understanding the brand angle, the trend lifecycle, and platform pacing. The Orchestrator does this well — no sub-agent needed.
- **Strict 7-item constraint**: The tool schema uses `minItems: 7, maxItems: 7` to enforce exactly one week of content. The Orchestrator cannot short-change the calendar.
- **Saved separately**: The `.txt` calendar file in `output/calendars/` makes it usable by a social media manager without opening the campaign JSON.
