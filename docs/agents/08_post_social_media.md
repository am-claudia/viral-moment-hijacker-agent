# Task 8 — POST: Publish to Social Media

## Agent: Simulated Tool (no sub-agent)

| Property | Value |
|---|---|
| **File** | `src/tools.py` → `post_to_social_media()` |
| **Model** | None — pure Python function |
| **Triggered by** | `post_to_social_media` tool call from the Orchestrator |
| **Type** | Simulated publish (no real API call) |

---

## What It Does

Simulates publishing the reactive brand post (written in Task 6) to the brand's social media account. It generates a realistic-looking post URL and estimated reach, and returns a confirmation the Orchestrator can include in the final campaign save.

In production, this function would call the platform's actual publishing API. The simulation is intentional for the demo context.

---

## Inputs

The Orchestrator calls `post_to_social_media` with the brand post it wrote in Task 6:

```json
{
  "platform": "TikTok",
  "post_content": "25 days. 25 dinners you actually looked forward to...",
  "post_type": "reel"
}
```

`post_type` is optional — defaults to `"feed"`.

---

## Outputs

```json
{
  "success": true,
  "platform": "TikTok",
  "post_id": "abc123xyz89",
  "post_url": "https://www.tiktok.com/@brand/video/abc123xyz89",
  "post_type": "reel",
  "character_count": 187,
  "status": "published",
  "estimated_reach": "12.4K",
  "note": "[SIMULATED] In production, calls the platform's publishing API."
}
```

The `post_url` is passed to `save_campaign_results` as `social_post_url` and displayed in the CLI output.

---

## URL Templates by Platform

| Platform | URL Format |
|---|---|
| Instagram | `https://www.instagram.com/p/{post_id}/` |
| TikTok | `https://www.tiktok.com/@brand/video/{post_id}` |
| LinkedIn | `https://www.linkedin.com/posts/{post_id}` |
| Twitter | `https://twitter.com/brand/status/{post_id}` |

`post_id` is an 11-character random alphanumeric string.

---

## Why This Design

- **No sub-agent**: Publishing is a deterministic API call — it doesn't involve reasoning or content generation. A Claude sub-agent would add cost and latency for zero benefit.
- **Simulated, not mocked**: The simulation returns realistic data (post URL, estimated reach) so the rest of the pipeline (save, display) behaves exactly as it would in production.
- **Easy to make real**: Replace the simulation block with a call to the platform's API. The tool's inputs and outputs don't change — the Orchestrator never needs to know.
