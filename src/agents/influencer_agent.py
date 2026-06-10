import json
import os
import anthropic
from apify_client import ApifyClient
from ..config import INFLUENCER_AGENT_MODEL


def _fmt(n: int) -> str:
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.0f}K"
    return str(n)


def _scrape_tiktok_creators(trend: str, count: int) -> list:
    token = os.environ.get("APIFY_API_TOKEN")
    if not token:
        raise ValueError("APIFY_API_TOKEN not set in .env")
    client = ApifyClient(token)
    hashtag = trend.lower().replace("#", "").replace(" ", "")
    run = client.actor("clockworks/tiktok-scraper").call(run_input={
        "hashtags": [hashtag],
        "resultsPerPage": 30,
        "shouldDownloadVideos": False,
        "shouldDownloadCovers": False,
    })
    items = list(client.dataset(run.default_dataset_id).iterate_items())
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
    top = sorted(creators, key=lambda x: x["followers_raw"], reverse=True)[:count * 2]
    for c in top:
        c["followers"] = _fmt(c.pop("followers_raw"))
        c["video_views"] = _fmt(c["video_views"])
        c["video_likes"] = _fmt(c["video_likes"])
    return top


def run_influencer_agent(trend: str, platform: str, niche: str, count: int = 3) -> str:
    """
    InfluencerAgent — a specialized sub-agent for creator identification and evaluation.

    Step 1: Scrapes real creator profiles from Apify who are posting about the trend.
    Step 2: Uses Claude to score each creator on brand fit and return the best matches.

    The orchestrator calls this via the find_influencers tool and receives
    pre-evaluated profiles with fit scores — not raw scraped data.
    """
    # Step 1: Scrape real creator data from TikTok
    try:
        raw_creators = _scrape_tiktok_creators(trend, count * 3)
    except Exception as e:
        return json.dumps({"error": str(e), "trend": trend, "platform": platform})

    raw_json = json.dumps(raw_creators[: count * 2], ensure_ascii=False)

    # Step 2: Claude evaluates and ranks creators by niche fit and engagement quality
    client = anthropic.Anthropic()
    response = client.messages.create(
        model=INFLUENCER_AGENT_MODEL,
        max_tokens=1024,
        system=(
            f"You are an influencer marketing analyst specializing in {niche} on {platform}. "
            "You evaluate creator profiles and recommend the best ones for brand partnerships.\n\n"
            "For each creator output:\n"
            "- name, handle, followers, verified, platform (copy from input)\n"
            "- fit_score: 1-10 (10 = perfect match for this niche and trend)\n"
            "- why_good_fit: one sentence on WHY they're a strong partner for this campaign\n"
            "- content_style: one word (e.g., 'educational', 'humorous', 'aspirational')\n"
            "- recent_trend_post: first 150 chars of their trend post (copy from input)\n\n"
            f'Return ONLY valid JSON: {{"trend": "...", "platform": "...", "niche": "...", "influencers": [top {count}]}}'
        ),
        messages=[{
            "role": "user",
            "content": (
                f"Evaluate these {platform} creators posting about '{trend}' in the {niche} niche:\n\n"
                f"{raw_json}\n\n"
                f"Return the top {count} ranked by fit_score."
            ),
        }],
    )

    return response.content[0].text
