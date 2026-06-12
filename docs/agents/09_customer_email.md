# Task 9 — EMAIL: Send Customer Email

## Agent: EmailAgent

| Property | Value |
|---|---|
| **File** | `src/agents/email_agent.py` |
| **Model** | `gemini-2.5-pro` |
| **Triggered by** | `send_customer_email` tool call from the Orchestrator |
| **Type** | Single-turn sub-agent |

---

## What It Does

The EmailAgent writes a complete, trend-inspired customer email and simulates sending it to the brand's subscriber list. The Orchestrator does **not** write any email copy — it only provides trend context and the brand angle, then the EmailAgent handles all copywriting.

It runs in **two steps**:

1. **Write** — Gemini Pro generates a full email: subject line, body, featured product, and CTA
2. **Simulate** — generates subscriber stats and saves a plain-text preview to `output/emails/`

---

## Inputs

The Orchestrator calls `send_customer_email` with only trend context:

```json
{
  "trend_name": "25-Day Gym Streak Challenge",
  "trend_summary": "Fitness creators are documenting daily gym visits and tagging their meals...",
  "brand_angle": "Forkly makes the gym streak sustainable — quick, nutritious meal kits for people who move"
}
```

Brand context (`brand_name`, `brand_description`, `tone`) is **injected by the tool dispatcher** in `execute_tool()` from the `ViralMomentHijacker` instance — the Orchestrator does not pass it explicitly. This keeps the tool's input schema clean.

---

## Outputs

Returns a JSON string with the complete email and send stats:

```json
{
  "success": true,
  "subject": "Your streak deserves the right fuel 🔥",
  "trend": "25-Day Gym Streak Challenge",
  "featured_item": "The Power Prep Kit — 5 high-protein dinners, 30 min each",
  "cta_text": "Fuel my next streak",
  "trend_connection": "The viral gym streak trend shows that habit-builders want meals that keep up with their goals",
  "email_body": "Hey Forkly fam,\n\nBy now you've probably seen the #gymstreak challenge all over TikTok...",
  "subscribers_reached": 14200,
  "estimated_open_rate": "31%",
  "estimated_clicks": 789,
  "email_preview_saved": "output/emails/email_20260611_143022.txt",
  "status": "sent",
  "note": "[SIMULATED] In production, calls SendGrid / Mailchimp / Klaviyo API."
}
```

The `subject` and `subscribers_reached` fields are passed to `save_campaign_results` as `customer_email_subject` and `customer_email_subscribers`.

---

## How It Works

```
send_customer_email(trend_name, trend_summary, brand_angle)
        │  (+ brand_name, brand_description, tone injected by dispatcher)
        ▼
client.models.generate_content(       ← Gemini Pro
    model = EMAIL_AGENT_MODEL,
    contents = trend_context,
    config = GenerateContentConfig(system_instruction="You are an email marketing specialist for {brand_name}...")
)
        │
        ▼
email_data = json.loads(response)     ← subject, body, featured_item, cta_text
        │
        ▼
Simulate stats (random subscriber count 8K–30K, open rate 22–41%)
        │
        ▼
Save preview → output/emails/email_<timestamp>.txt
        │
        ▼
Returns: JSON string → Orchestrator
```

---

## Why Pro (Not Flash)?

Email copywriting is customer-facing creative writing. The quality of the subject line and email body directly affects open rates and conversions. Gemini Pro produces more natural, compelling copy than Flash — the cost difference is worth it for this task.

Compare to the Trend and Influencer agents, which do structured JSON classification from scraped data — Flash is sufficient there.

---

## Why a Sub-Agent?

Email copywriting is a distinct creative task with its own context requirements (brand voice, email conventions, CTA formatting). Delegating it to a sub-agent keeps the Orchestrator focused on campaign strategy and avoids polluting its reasoning with email format concerns. The Orchestrator treats email as a black box — it provides context and gets back a send confirmation.
