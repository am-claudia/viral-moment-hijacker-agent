import json
import os
import datetime

from .agents import run_trend_agent, run_influencer_agent, run_email_agent

# ---------------------------------------------------------------------------
# Tool schemas — what the orchestrator (Claude Opus) sees and can call
# ---------------------------------------------------------------------------

TOOL_SCHEMAS = [
    {
        "name": "search_viral_trends",
        "description": (
            "Delegate to the TrendResearchAgent to find what's going viral on the target platform. "
            "The agent scrapes live data via Apify, then analyzes and ranks trends by opportunity score. "
            "Returns pre-analyzed results with content angles — not raw hashtag data."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "industry": {
                    "type": "string",
                    "description": "The industry or niche to search (e.g., 'food', 'fitness', 'beauty', 'fintech')"
                },
                "timeframe": {
                    "type": "string",
                    "enum": ["last 24 hours", "last 48 hours", "this week"],
                    "description": "How far back to look for trends"
                },
            },
            "required": ["industry", "timeframe"],
        },
    },
    {
        "name": "find_influencers",
        "description": (
            "Delegate to the InfluencerAgent to find creators actively posting about the trend. "
            "The agent scrapes real profiles from Apify, scores each on niche fit and engagement quality, "
            "and returns ranked, ready-to-pitch profiles with a fit_score and why_good_fit explanation."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "trend": {
                    "type": "string",
                    "description": "The trending topic or hashtag to search for"
                },
                "platform": {
                    "type": "string",
                    "enum": ["Instagram", "TikTok", "LinkedIn", "Twitter"],
                    "description": "Social media platform to search on"
                },
                "niche": {
                    "type": "string",
                    "description": "Specific niche within the industry (e.g., 'home cooking', 'meal prep')"
                },
                "count": {
                    "type": "integer",
                    "default": 3,
                    "description": "Number of influencers to return (default: 3)"
                },
            },
            "required": ["trend", "platform", "niche"],
        },
    },
    {
        "name": "send_customer_email",
        "description": (
            "Delegate to the EmailAgent to write and send a trend-inspired customer email. "
            "Provide the trend context and brand angle — the agent handles all copywriting. "
            "Do NOT write the email yourself; just pass the trend details and let the agent do it."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "trend_name": {
                    "type": "string",
                    "description": "The viral trend this email is responding to"
                },
                "trend_summary": {
                    "type": "string",
                    "description": "2-3 sentence summary of why this trend is going viral and what people are saying"
                },
                "brand_angle": {
                    "type": "string",
                    "description": "The specific angle the brand is taking to join this trend authentically"
                },
            },
            "required": ["trend_name", "trend_summary", "brand_angle"],
        },
    },
    {
        "name": "post_to_social_media",
        "description": (
            "Publish the reactive brand post to the company's own social media account. "
            "Call this after writing the brand post. Returns the post URL and estimated reach."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "platform": {
                    "type": "string",
                    "description": "Platform to post on (Instagram, TikTok, LinkedIn, Twitter)"
                },
                "post_content": {
                    "type": "string",
                    "description": "The full post content including caption and hashtags"
                },
                "post_type": {
                    "type": "string",
                    "enum": ["feed", "story", "reel", "short"],
                    "description": "Type of post — reel or short for video-first platforms, feed otherwise"
                },
            },
            "required": ["platform", "post_content"],
        },
    },
    {
        "name": "generate_hashtag_strategy",
        "description": (
            "Generate a grouped hashtag strategy for the campaign. "
            "Call this after identifying the trend and platform. "
            "You provide the hashtags — this tool formats and returns them ready to use."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "broad": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "3-5 high-volume hashtags (1M+ posts) for reach e.g. #food #cooking"
                },
                "niche": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "4-6 mid-size hashtags (10K-500K posts) for targeted engagement"
                },
                "branded": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "1-2 brand-owned hashtags"
                },
                "trend": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "3-5 trend-specific hashtags tied to the viral moment"
                },
                "caption_formula": {
                    "type": "string",
                    "description": "One-sentence guide on how to combine these groups per post"
                },
            },
            "required": ["broad", "niche", "branded", "trend", "caption_formula"],
        },
    },
    {
        "name": "generate_content_calendar",
        "description": (
            "Save a 7-day content calendar built around the viral trend. "
            "Call this after choosing the brand angle and before saving final results. "
            "You provide the full calendar — this tool formats and saves it."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "days": {
                    "type": "array",
                    "description": "7 days of planned content",
                    "items": {
                        "type": "object",
                        "properties": {
                            "day": {"type": "string"},
                            "format": {"type": "string"},
                            "caption": {"type": "string"},
                            "optimal_time": {"type": "string"},
                        },
                        "required": ["day", "format", "caption", "optimal_time"],
                    },
                    "minItems": 7,
                    "maxItems": 7,
                },
            },
            "required": ["days"],
        },
    },
    {
        "name": "save_campaign_results",
        "description": (
            "Save the complete campaign package to disk. "
            "Call this at the very end after all content is created and distributed."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "viral_trend": {"type": "string"},
                "trend_summary": {"type": "string"},
                "brand_angle": {"type": "string"},
                "influencer_pitches": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "handle": {"type": "string"},
                            "followers": {"type": "string"},
                            "dm_pitch": {"type": "string"},
                        },
                        "required": ["name", "handle", "dm_pitch"],
                    },
                },
                "brand_post": {"type": "string"},
                "platform": {"type": "string"},
                "social_post_url": {"type": "string"},
                "customer_email_subject": {"type": "string"},
                "customer_email_subscribers": {"type": "integer"},
                "content_calendar": {"type": "array", "items": {"type": "object"}},
                "hashtag_strategy": {"type": "object"},
            },
            "required": ["viral_trend", "trend_summary", "brand_angle", "influencer_pitches", "brand_post", "platform"],
        },
    },
]


# ---------------------------------------------------------------------------
# Tool implementations — each delegates to a sub-agent or runs directly
# ---------------------------------------------------------------------------

def search_viral_trends(industry: str, timeframe: str, platform: str) -> str:
    """Delegates to TrendResearchAgent: scrape + analyze live trend data."""
    return run_trend_agent(industry=industry, timeframe=timeframe, platform=platform)


def find_influencers(trend: str, platform: str, niche: str, count: int = 3) -> str:
    """Delegates to InfluencerAgent: scrape + evaluate real creator profiles."""
    return run_influencer_agent(trend=trend, platform=platform, niche=niche, count=count)


def send_customer_email(
    trend_name: str,
    trend_summary: str,
    brand_angle: str,
    platform: str,
    brand_name: str,
    brand_description: str,
    tone: str,
) -> str:
    """Delegates to EmailAgent: write the full email copy, then simulate sending."""
    return run_email_agent(
        trend_name=trend_name,
        trend_summary=trend_summary,
        brand_angle=brand_angle,
        platform=platform,
        brand_name=brand_name,
        brand_description=brand_description,
        tone=tone,
    )


def post_to_social_media(platform: str, post_content: str, post_type: str = "feed") -> str:
    """Simulate publishing a post to the brand's social media account."""
    import random
    import string

    post_id = "".join(random.choices(string.ascii_lowercase + string.digits, k=11))
    platform_url_templates = {
        "Instagram": f"https://www.instagram.com/p/{post_id}/",
        "TikTok": f"https://www.tiktok.com/@brand/video/{post_id}",
        "LinkedIn": f"https://www.linkedin.com/posts/{post_id}",
        "Twitter": f"https://twitter.com/brand/status/{post_id}",
    }
    post_url = platform_url_templates.get(platform, f"https://{platform.lower()}.com/p/{post_id}")

    return json.dumps({
        "success": True,
        "platform": platform,
        "post_id": post_id,
        "post_url": post_url,
        "post_type": post_type,
        "character_count": len(post_content),
        "status": "published",
        "estimated_reach": f"{random.randint(2, 18)}.{random.randint(1, 9)}K",
        "note": "[SIMULATED] In production, calls the platform's publishing API.",
    })


def generate_content_calendar(days: list) -> str:
    """Return the 7-day content calendar (saved together with campaign at the end)."""
    return json.dumps({
        "success": True,
        "days_planned": len(days),
        "calendar": days,
    }, ensure_ascii=False)


def generate_hashtag_strategy(
    broad: list, niche: list, branded: list, trend: list, caption_formula: str
) -> str:
    """Return the grouped hashtag strategy (saved together with campaign at the end)."""
    all_tags = broad + niche + branded + trend
    return json.dumps({
        "success": True,
        "groups": {"broad": broad, "niche": niche, "branded": branded, "trend": trend},
        "caption_formula": caption_formula,
        "full_set": " ".join(all_tags),
        "total_tags": len(all_tags),
    }, ensure_ascii=False)


def save_campaign_results(
    viral_trend: str,
    trend_summary: str,
    brand_angle: str,
    influencer_pitches: list,
    brand_post: str,
    platform: str,
    brand_name: str,
    social_post_url: str = None,
    customer_email_subject: str = None,
    customer_email_subscribers: int = None,
    content_calendar: list = None,
    hashtag_strategy: dict = None,
) -> str:
    """Persist the complete campaign package to output/."""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_brand = brand_name.lower().replace(" ", "_")

    os.makedirs("output/campaigns", exist_ok=True)
    os.makedirs("output/calendars", exist_ok=True)
    os.makedirs("output/hashtags", exist_ok=True)

    campaign_file = f"output/campaigns/campaign_{safe_brand}_{timestamp}.json"
    calendar_file = f"output/calendars/calendar_{safe_brand}_{timestamp}.txt"
    hashtags_file = f"output/hashtags/hashtags_{safe_brand}_{timestamp}.txt"

    campaign = {
        "metadata": {
            "brand": brand_name,
            "platform": platform,
            "generated_at": datetime.datetime.now().isoformat(),
        },
        "viral_trend": viral_trend,
        "trend_summary": trend_summary,
        "brand_angle": brand_angle,
        "influencer_pitches": influencer_pitches,
        "brand_post": brand_post,
        "distribution": {
            "social_post_url": social_post_url,
            "customer_email_subject": customer_email_subject,
            "customer_email_subscribers": customer_email_subscribers,
        },
        "content_calendar": content_calendar or [],
        "hashtag_strategy": hashtag_strategy or {},
    }
    with open(campaign_file, "w", encoding="utf-8") as f:
        json.dump(campaign, f, indent=2, ensure_ascii=False)

    if content_calendar:
        lines = ["7-DAY CONTENT CALENDAR", "=" * 50, ""]
        for entry in content_calendar:
            lines += [
                f"📅 {entry.get('day', '').upper()}",
                f"   Format : {entry.get('format', '')}",
                f"   Time   : {entry.get('optimal_time', '')}",
                f"   Caption: {entry.get('caption', '')}",
                "",
            ]
        with open(calendar_file, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

    if hashtag_strategy:
        groups = hashtag_strategy.get("groups") or hashtag_strategy
        formula = hashtag_strategy.get("caption_formula", "")
        full_set = hashtag_strategy.get("full_set", "")
        lines = [
            "HASHTAG STRATEGY", "=" * 50, "",
            f"BROAD   : {' '.join(groups.get('broad', []))}",
            f"NICHE   : {' '.join(groups.get('niche', []))}",
            f"BRANDED : {' '.join(groups.get('branded', []))}",
            f"TREND   : {' '.join(groups.get('trend', []))}",
            "", f"FORMULA : {formula}", "", f"FULL SET: {full_set}",
        ]
        with open(hashtags_file, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

    return json.dumps({
        "success": True,
        "saved_to": campaign_file,
        "campaign_id": f"{safe_brand}_{timestamp}",
    })


# ---------------------------------------------------------------------------
# Tool dispatcher — called by the orchestrator's agentic loop
# ---------------------------------------------------------------------------

def execute_tool(
    tool_name: str,
    tool_input: dict,
    brand_name: str,
    platform: str,
    brand_description: str = "",
    tone: str = "casual",
) -> str:
    """Dispatch a tool call to its implementation (sub-agent or direct function)."""
    if tool_name == "search_viral_trends":
        return search_viral_trends(
            industry=tool_input["industry"],
            timeframe=tool_input.get("timeframe", "last 24 hours"),
            platform=platform,
        )

    if tool_name == "find_influencers":
        return find_influencers(
            trend=tool_input["trend"],
            platform=tool_input["platform"],
            niche=tool_input["niche"],
            count=tool_input.get("count", 3),
        )

    if tool_name == "send_customer_email":
        # Brand context (name, description, tone) is injected here from the orchestrator instance.
        # The orchestrator only provides trend context — the EmailAgent handles all copywriting.
        return send_customer_email(
            trend_name=tool_input["trend_name"],
            trend_summary=tool_input["trend_summary"],
            brand_angle=tool_input["brand_angle"],
            platform=platform,
            brand_name=brand_name,
            brand_description=brand_description,
            tone=tone,
        )

    if tool_name == "post_to_social_media":
        return post_to_social_media(
            platform=tool_input.get("platform", platform),
            post_content=tool_input["post_content"],
            post_type=tool_input.get("post_type", "feed"),
        )

    if tool_name == "generate_content_calendar":
        return generate_content_calendar(days=tool_input["days"])

    if tool_name == "generate_hashtag_strategy":
        return generate_hashtag_strategy(
            broad=tool_input["broad"],
            niche=tool_input["niche"],
            branded=tool_input["branded"],
            trend=tool_input["trend"],
            caption_formula=tool_input["caption_formula"],
        )

    if tool_name == "save_campaign_results":
        return save_campaign_results(
            viral_trend=tool_input["viral_trend"],
            trend_summary=tool_input["trend_summary"],
            brand_angle=tool_input["brand_angle"],
            influencer_pitches=tool_input["influencer_pitches"],
            brand_post=tool_input["brand_post"],
            platform=tool_input["platform"],
            brand_name=brand_name,
            social_post_url=tool_input.get("social_post_url"),
            customer_email_subject=tool_input.get("customer_email_subject"),
            customer_email_subscribers=tool_input.get("customer_email_subscribers"),
            content_calendar=tool_input.get("content_calendar"),
            hashtag_strategy=tool_input.get("hashtag_strategy"),
        )

    return json.dumps({"error": f"Unknown tool: {tool_name}"})
