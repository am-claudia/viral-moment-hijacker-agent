import json
import os
import datetime

import praw
import tweepy
from pytrends.request import TrendReq
from apify_client import ApifyClient

TOOL_SCHEMAS = [
    {
        "name": "post_to_social_media",
        "description": (
            "Publish the reactive brand post to the company's own social media account on the target platform. "
            "Call this after writing the brand post. Returns the post URL and an estimated reach."
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
                }
            },
            "required": ["platform", "post_content"]
        }
    },
    {
        "name": "send_customer_email",
        "description": (
            "Send a trend-inspired marketing email to the brand's customer list. "
            "The email should connect the viral trend to a concrete customer action. "
            "For a meal kit brand: tie the trend to a specific recipe customers can add to their next delivery. "
            "For other brands: tie the trend to a relevant product or offer. "
            "Write a punchy subject line, a full email body, and a clear CTA."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "subject": {
                    "type": "string",
                    "description": "Email subject line — keep it under 60 characters for good open rates"
                },
                "email_body": {
                    "type": "string",
                    "description": (
                        "Full email body — conversational tone, references the viral trend, "
                        "features the product/recipe/offer, and leads naturally to the CTA"
                    )
                },
                "trend_name": {
                    "type": "string",
                    "description": "The viral trend this email is responding to"
                },
                "featured_item": {
                    "type": "string",
                    "description": "The specific recipe, product, or offer being highlighted (e.g., 'Spicy Miso Ramen Kit')"
                },
                "cta_text": {
                    "type": "string",
                    "description": "Call-to-action button text, e.g. 'Add to my next kit' or 'Shop the look'"
                }
            },
            "required": ["subject", "email_body", "trend_name", "featured_item", "cta_text"]
        }
    },
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
                },
                "social_post_url": {
                    "type": "string",
                    "description": "URL of the published social post (from post_to_social_media result)"
                },
                "customer_email_subject": {
                    "type": "string",
                    "description": "Subject line of the customer email that was sent"
                },
                "customer_email_subscribers": {
                    "type": "integer",
                    "description": "Number of subscribers the email was sent to"
                }
            },
            "required": ["viral_trend", "trend_summary", "brand_angle", "influencer_pitches", "brand_post", "platform"]
        }
    }
]


# Maps the tool's timeframe enum to each API's native format
_TIMEFRAME = {
    "last 24 hours": {"pytrends": "now 1-d",  "reddit": "day"},
    "last 48 hours": {"pytrends": "now 2-d",  "reddit": "week"},
    "this week":     {"pytrends": "now 7-d",  "reddit": "week"},
}


def _fmt(n: int) -> str:
    """Turn a raw integer into a readable count (1.2M, 245K, etc.)."""
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.0f}K"
    return str(n)


# ── Google Trends ─────────────────────────────────────────────────────────────

def _google_trends(industry: str, timeframe: str) -> list:
    try:
        pt_tf = _TIMEFRAME.get(timeframe, {}).get("pytrends", "now 1-d")
        pytrends = TrendReq(hl="en-US", tz=360)

        pytrends.build_payload([industry], timeframe=pt_tf)
        related = pytrends.related_queries()

        results = []
        top = related.get(industry, {}).get("top")
        if top is not None and not top.empty:
            for _, row in top.head(5).iterrows():
                results.append({
                    "trend": row["query"],
                    "relevance_score": int(row["value"]),
                    "source": "google_trends",
                })

        # Also pull US real-time trending searches and filter by industry keyword
        trending = pytrends.trending_searches(pn="united_states")
        for term in trending[0].head(20).tolist():
            if any(kw in term.lower() for kw in industry.lower().split()):
                results.append({"trend": term, "relevance_score": 100, "source": "google_trends_realtime"})

        return results
    except Exception as e:
        return [{"error": f"Google Trends: {e}"}]


# ── Reddit ────────────────────────────────────────────────────────────────────

def _reddit_trends(industry: str, timeframe: str) -> list:
    client_id = os.environ.get("REDDIT_CLIENT_ID")
    client_secret = os.environ.get("REDDIT_CLIENT_SECRET")
    if not client_id or not client_secret:
        return [{"error": "REDDIT_CLIENT_ID / REDDIT_CLIENT_SECRET not set in .env"}]

    try:
        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent="ViralMomentHijacker/1.0",
        )
        time_filter = _TIMEFRAME.get(timeframe, {}).get("reddit", "day")
        results = []
        for post in reddit.subreddit("all").search(
            query=industry, sort="hot", time_filter=time_filter, limit=15
        ):
            results.append({
                "trend": post.title,
                "subreddit": f"r/{post.subreddit.display_name}",
                "score": post.score,
                "comments": post.num_comments,
                "url": post.url,
                "source": "reddit",
            })
        return results
    except Exception as e:
        return [{"error": f"Reddit: {e}"}]


# ── Twitter/X ─────────────────────────────────────────────────────────────────

def _twitter_trends(industry: str) -> list:
    bearer_token = os.environ.get("TWITTER_BEARER_TOKEN")
    if not bearer_token:
        return [{"error": "TWITTER_BEARER_TOKEN not set in .env — skipping Twitter"}]

    try:
        client = tweepy.Client(bearer_token=bearer_token, wait_on_rate_limit=False)
        response = client.search_recent_tweets(
            query=f"{industry} -is:retweet lang:en",
            max_results=10,
            tweet_fields=["public_metrics", "created_at"],
            sort_order="relevancy",
        )
        results = []
        if response.data:
            for tweet in response.data:
                m = tweet.public_metrics
                results.append({
                    "text": tweet.text[:280],
                    "likes": m["like_count"],
                    "retweets": m["retweet_count"],
                    "source": "twitter",
                })
        return results
    except tweepy.errors.Forbidden:
        return [{"error": "Twitter free tier does not support search. Needs Basic plan ($100/month)."}]
    except Exception as e:
        return [{"error": f"Twitter: {e}"}]


# ── Apify TikTok ──────────────────────────────────────────────────────────────

def _apify_tiktok(trend: str, count: int) -> list:
    api_token = os.environ.get("APIFY_API_TOKEN")
    if not api_token:
        raise ValueError("APIFY_API_TOKEN not set in .env")

    client = ApifyClient(api_token)
    hashtag = trend.lower().replace("#", "").replace(" ", "")

    run = client.actor("clockworks/tiktok-scraper").call(run_input={
        "hashtags": [hashtag],
        "resultsPerPage": 30,
        "shouldDownloadVideos": False,
        "shouldDownloadCovers": False,
    })

    items = list(client.dataset(run["defaultDatasetId"]).iterate_items())

    seen = set()
    creators = []
    for item in items:
        author = item.get("authorMeta", {})
        handle = author.get("name", "")
        if not handle or handle in seen:
            continue
        seen.add(handle)
        creators.append({
            "name": author.get("nickName", handle),
            "handle": f"@{handle}",
            "platform": "TikTok",
            "followers_raw": author.get("fans", 0),
            "verified": author.get("verified", False),
            "bio": author.get("signature", "")[:150],
            "recent_trend_post": item.get("text", "")[:200],
            "video_views": item.get("playCount", 0),
            "video_likes": item.get("diggCount", 0),
        })

    top = sorted(creators, key=lambda x: x["followers_raw"], reverse=True)[:count]
    for c in top:
        c["followers"] = _fmt(c.pop("followers_raw"))
        c["video_views"] = _fmt(c["video_views"])
        c["video_likes"] = _fmt(c["video_likes"])

    return top


# ── Public tool functions ─────────────────────────────────────────────────────

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
        "note": "[SIMULATED] In production, calls the platform's publishing API (Instagram Graph API, TikTok Business API, etc.).",
    })


def send_customer_email(
    subject: str,
    email_body: str,
    trend_name: str,
    featured_item: str,
    cta_text: str,
) -> str:
    """Simulate sending a trend-inspired email to the customer list and save a preview."""
    import random

    subscriber_count = random.randint(8_000, 30_000)
    open_rate = random.randint(22, 41)
    estimated_clicks = int(subscriber_count * (open_rate / 100) * random.uniform(0.08, 0.18))

    os.makedirs("output/emails", exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    preview_file = f"output/emails/email_{timestamp}.txt"

    preview = (
        f"SUBJECT : {subject}\n"
        f"TREND   : {trend_name}\n"
        f"FEATURE : {featured_item}\n"
        f"CTA     : {cta_text}\n"
        f"SENT TO : {subscriber_count:,} subscribers\n"
        f"\n{'─' * 60}\n\n"
        f"{email_body}\n"
    )
    with open(preview_file, "w", encoding="utf-8") as f:
        f.write(preview)

    return json.dumps({
        "success": True,
        "subject": subject,
        "trend": trend_name,
        "featured_item": featured_item,
        "cta_text": cta_text,
        "subscribers_reached": subscriber_count,
        "estimated_open_rate": f"{open_rate}%",
        "estimated_clicks": estimated_clicks,
        "email_preview_saved": preview_file,
        "status": "sent",
        "note": "[SIMULATED] In production, calls SendGrid / Mailchimp / Klaviyo API.",
    })


def search_viral_trends(industry: str, timeframe: str) -> str:
    """Fetch real trend data from Google Trends, Reddit, and Twitter."""
    return json.dumps({
        "industry": industry,
        "timeframe": timeframe,
        "sources": {
            "google_trends": _google_trends(industry, timeframe),
            "reddit": _reddit_trends(industry, timeframe),
            "twitter": _twitter_trends(industry),
        },
    }, ensure_ascii=False)


def find_influencers(trend: str, platform: str, niche: str, count: int = 3) -> str:
    """Find real TikTok influencers via Apify's TikTok scraper."""
    influencers = _apify_tiktok(trend, count)
    return json.dumps({
        "trend": trend,
        "platform": platform,
        "niche": niche,
        "influencers": influencers,
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
        "distribution": {
            "social_post_url": social_post_url,
            "customer_email_subject": customer_email_subject,
            "customer_email_subscribers": customer_email_subscribers,
        },
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

    if tool_name == "post_to_social_media":
        return post_to_social_media(
            platform=tool_input.get("platform", platform),
            post_content=tool_input["post_content"],
            post_type=tool_input.get("post_type", "feed"),
        )

    if tool_name == "send_customer_email":
        return send_customer_email(
            subject=tool_input["subject"],
            email_body=tool_input["email_body"],
            trend_name=tool_input["trend_name"],
            featured_item=tool_input["featured_item"],
            cta_text=tool_input["cta_text"],
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
        )

    return json.dumps({"error": f"Unknown tool: {tool_name}"})
