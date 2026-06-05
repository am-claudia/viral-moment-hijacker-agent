import json
import os
import datetime
import anthropic

from .config import DATA_MODEL

TOOL_SCHEMAS = [
    {
        "name": "search_viral_trends",
        "description": (
            "Search for what's currently trending and going viral in a specific industry. "
            "Returns ranked trending topics with engagement data, sentiment, and opportunity scores."
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
                }
            },
            "required": ["industry", "timeframe"]
        }
    },
    {
        "name": "find_influencers",
        "description": (
            "Find social media influencers actively posting about a specific trend. "
            "Returns profiles with follower counts, engagement rates, content style, and recent relevant posts."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "trend": {
                    "type": "string",
                    "description": "The trending topic or challenge to search for"
                },
                "platform": {
                    "type": "string",
                    "enum": ["Instagram", "TikTok", "LinkedIn", "Twitter"],
                    "description": "Social media platform to search on"
                },
                "niche": {
                    "type": "string",
                    "description": "Specific niche within the industry (e.g., 'home cooking', 'meal prep', 'food photography')"
                },
                "count": {
                    "type": "integer",
                    "default": 3,
                    "description": "Number of influencers to return (default: 3)"
                }
            },
            "required": ["trend", "platform", "niche"]
        }
    },
    {
        "name": "save_campaign_results",
        "description": (
            "Save the complete campaign package to disk. "
            "Call this at the very end after creating all content: angle, DM pitches, and brand post."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "viral_trend": {
                    "type": "string",
                    "description": "The selected viral trend name or title"
                },
                "trend_summary": {
                    "type": "string",
                    "description": "Concise summary of the trend, why it's viral, and what people are saying"
                },
                "brand_angle": {
                    "type": "string",
                    "description": "The specific angle the brand takes to authentically join the conversation"
                },
                "influencer_pitches": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "handle": {"type": "string"},
                            "followers": {"type": "string"},
                            "dm_pitch": {"type": "string"}
                        },
                        "required": ["name", "handle", "dm_pitch"]
                    },
                    "description": "List of influencers with their personalized DM pitches"
                },
                "brand_post": {
                    "type": "string",
                    "description": "The reactive brand post copy — caption, hashtags, everything"
                },
                "platform": {
                    "type": "string",
                    "description": "The social media platform this campaign targets"
                }
            },
            "required": ["viral_trend", "trend_summary", "brand_angle", "influencer_pitches", "brand_post", "platform"]
        }
    }
]


def search_viral_trends(industry: str, timeframe: str) -> str:
    """Generate realistic trending topics using Haiku."""
    client = anthropic.Anthropic()

    prompt = f"""Generate a realistic JSON response for what's trending in the {industry} industry over the {timeframe}.

Return ONLY valid JSON with this exact structure:
{{
  "industry": "{industry}",
  "timeframe": "{timeframe}",
  "trending_topics": [
    {{
      "trend": "Specific Trend or Challenge Name",
      "hashtags": ["#HashTag1", "#HashTag2", "#HashTag3"],
      "estimated_posts": "142K",
      "sentiment": "highly positive",
      "opportunity_level": "high",
      "why_viral": "Specific reason this is blowing up right now",
      "key_formats": ["Reel", "Carousel", "Story"]
    }}
  ]
}}

Create 3-4 realistic, specific trends. Make them feel current and grounded — specific challenge names, real-sounding hashtags, concrete reasons for virality. Not generic."""

    response = client.messages.create(
        model=DATA_MODEL,
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text


def find_influencers(trend: str, platform: str, niche: str, count: int = 3) -> str:
    """Generate realistic influencer profiles using Haiku."""
    client = anthropic.Anthropic()

    prompt = f"""Generate a realistic JSON array of {count} {platform} influencers actively posting about "{trend}" in the {niche} niche.

Return ONLY a valid JSON array:
[
  {{
    "name": "Full Name",
    "handle": "@handle",
    "platform": "{platform}",
    "followers": "245K",
    "engagement_rate": "7.8%",
    "content_style": "Short description of their posting style and personality",
    "niche": "{niche}",
    "location": "City, Country",
    "recent_trend_post": "Specific description of a recent post they made about {trend}",
    "why_relevant": "Why this creator is a great fit for a brand collab"
  }}
]

Make these feel like real creators. Realistic follower counts (10K–2M), distinct voices and styles. Each creator should be clearly different from the others."""

    response = client.messages.create(
        model=DATA_MODEL,
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text


def save_campaign_results(
    viral_trend: str,
    trend_summary: str,
    brand_angle: str,
    influencer_pitches: list,
    brand_post: str,
    platform: str,
    brand_name: str,
) -> str:
    """Persist the campaign package to output/."""
    os.makedirs("output", exist_ok=True)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_brand = brand_name.lower().replace(" ", "_")
    filename = f"output/campaign_{safe_brand}_{timestamp}.json"

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
    }

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(campaign, f, indent=2, ensure_ascii=False)

    return json.dumps({
        "success": True,
        "saved_to": filename,
        "campaign_id": f"{safe_brand}_{timestamp}",
    })


def execute_tool(tool_name: str, tool_input: dict, brand_name: str, platform: str) -> str:
    """Dispatch tool calls to their implementations."""
    if tool_name == "search_viral_trends":
        return search_viral_trends(
            industry=tool_input["industry"],
            timeframe=tool_input.get("timeframe", "last 24 hours"),
        )

    if tool_name == "find_influencers":
        return find_influencers(
            trend=tool_input["trend"],
            platform=tool_input["platform"],
            niche=tool_input["niche"],
            count=tool_input.get("count", 3),
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
        )

    return json.dumps({"error": f"Unknown tool: {tool_name}"})
