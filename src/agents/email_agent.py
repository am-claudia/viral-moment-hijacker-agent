import json
import os
import random
import datetime
import anthropic
from ..config import EMAIL_AGENT_MODEL


def run_email_agent(
    trend_name: str,
    trend_summary: str,
    brand_angle: str,
    platform: str,
    brand_name: str,
    brand_description: str,
    tone: str,
) -> str:
    """
    EmailAgent — a specialized sub-agent for customer email copywriting.

    The orchestrator delegates email writing entirely to this agent.
    It receives only the trend context and brand info, then:
      Step 1: Uses Claude to write a complete email (subject, body, CTA).
      Step 2: Simulates sending it and saves a preview to output/emails/.

    The orchestrator does NOT write the email itself — it just calls
    send_customer_email with trend context and gets back a sent confirmation.
    """
    # Step 1: Claude writes the complete email from trend + brand context
    client = anthropic.Anthropic()
    response = client.messages.create(
        model=EMAIL_AGENT_MODEL,
        max_tokens=1024,
        system=(
            f"You are an email marketing specialist for {brand_name}.\n"
            f"Brand: {brand_description}\n"
            f"Tone: {tone}\n\n"
            "Write a trend-inspired customer email that feels like a friendly heads-up, not a blast. "
            "Connect the viral trend to a specific, actionable product recommendation.\n\n"
            "Output ONLY valid JSON with these exact keys:\n"
            "- subject: punchy subject line under 60 characters\n"
            "- email_body: full email body — conversational, references the trend, one clear product recommendation, ends with CTA\n"
            "- featured_item: the specific product, recipe, or offer being highlighted\n"
            "- cta_text: button text like 'Add to my next kit' or 'Shop the look'\n"
            "- trend_connection: one sentence explaining how the email ties to the viral moment"
        ),
        messages=[{
            "role": "user",
            "content": (
                f"Write a customer email for {brand_name} based on this viral moment:\n\n"
                f"Trend: {trend_name}\n"
                f"Summary: {trend_summary}\n"
                f"Our brand angle: {brand_angle}\n"
                f"Platform: {platform}"
            ),
        }],
    )

    try:
        email_data = json.loads(response.content[0].text)
    except json.JSONDecodeError:
        return json.dumps({
            "error": "EmailAgent could not parse its own output as JSON",
            "raw": response.content[0].text[:500],
        })

    # Step 2: Simulate sending and save a plain-text preview
    subscriber_count = random.randint(8_000, 30_000)
    open_rate = random.randint(22, 41)
    estimated_clicks = int(subscriber_count * (open_rate / 100) * random.uniform(0.08, 0.18))

    os.makedirs("output/emails", exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    preview_file = f"output/emails/email_{timestamp}.txt"

    preview = (
        f"SUBJECT : {email_data.get('subject', '')}\n"
        f"TREND   : {trend_name}\n"
        f"FEATURE : {email_data.get('featured_item', '')}\n"
        f"CTA     : {email_data.get('cta_text', '')}\n"
        f"SENT TO : {subscriber_count:,} subscribers\n"
        f"\n{'─' * 60}\n\n"
        f"{email_data.get('email_body', '')}\n"
    )
    with open(preview_file, "w", encoding="utf-8") as f:
        f.write(preview)

    return json.dumps({
        "success": True,
        "subject": email_data.get("subject"),
        "trend": trend_name,
        "featured_item": email_data.get("featured_item"),
        "cta_text": email_data.get("cta_text"),
        "trend_connection": email_data.get("trend_connection"),
        "email_body": email_data.get("email_body"),
        "subscribers_reached": subscriber_count,
        "estimated_open_rate": f"{open_rate}%",
        "estimated_clicks": estimated_clicks,
        "email_preview_saved": preview_file,
        "status": "sent",
        "note": "[SIMULATED] In production, calls SendGrid / Mailchimp / Klaviyo API.",
    })
