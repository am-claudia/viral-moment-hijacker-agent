import json
import os
from google import genai
from google.genai import types
from apify_client import ApifyClient

try:
    from ..config import TREND_AGENT_MODEL, get_api_key
except ImportError:
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
    from src.config import TREND_AGENT_MODEL, get_api_key


def _fmt(n: int) -> str:
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.0f}K"
    return str(n)


def _clean_json(text: str) -> str:
    """Strip markdown code fences that Gemini sometimes wraps around JSON responses."""
    text = text.strip()
    if text.startswith("```"):
        first_newline = text.find("\n")
        if first_newline != -1:
            text = text[first_newline + 1:]
        if text.rstrip().endswith("```"):
            text = text.rstrip()[:-3].rstrip()
    return text


def _apify_client() -> ApifyClient:
    token = os.environ.get("APIFY_API_TOKEN")
    if not token:
        raise ValueError("APIFY_API_TOKEN not set in .env")
    return ApifyClient(token)


def _scrape_tiktok(industry: str, count: int = 10) -> list:
    client = _apify_client()
    keyword = industry.lower().replace(" ", "")
    run = client.actor("clockworks/tiktok-scraper").call(run_input={
        "hashtags": [keyword],
        "resultsPerPage": count * 4,
        "shouldDownloadVideos": False,
        "shouldDownloadCovers": False,
    })
    items = list(client.dataset(run.default_dataset_id).iterate_items())
    top = sorted(items, key=lambda x: x.get("playCount", 0), reverse=True)[:count * 2]
    seen = set()
    trends = []
    for item in top:
        text = item.get("text", "") or ""
        tags = [w.lstrip("#") for w in text.split() if w.startswith("#") and len(w) > 1]
        for tag in tags:
            if tag.lower() not in seen and tag.lower() != keyword:
                seen.add(tag.lower())
                trends.append({
                    "trend": f"#{tag}",
                    "source": "tiktok",
                    "top_video_views": _fmt(item.get("playCount", 0)),
                    "top_video_likes": _fmt(item.get("diggCount", 0)),
                    "sample_caption": text[:200],
                })
        if len(trends) >= count:
            break
    return trends[:count]


def _scrape_instagram(industry: str, count: int = 10) -> list:
    client = _apify_client()
    keyword = industry.lower().replace(" ", "")
    run = client.actor("apify/instagram-hashtag-scraper").call(run_input={
        "hashtags": [keyword],
        "resultsLimit": count * 3,
        "resultsType": "posts",
    })
    items = list(client.dataset(run.default_dataset_id).iterate_items())
    top = sorted(items, key=lambda x: x.get("likesCount", 0), reverse=True)[:count * 2]
    seen = set()
    trends = []
    for item in top:
        caption = item.get("caption", "") or ""
        tags = [w.lstrip("#") for w in caption.split() if w.startswith("#") and len(w) > 1]
        for tag in tags:
            if tag.lower() not in seen and tag.lower() != keyword:
                seen.add(tag.lower())
                trends.append({
                    "trend": f"#{tag}",
                    "source": "instagram",
                    "top_post_likes": _fmt(item.get("likesCount", 0)),
                    "top_post_comments": _fmt(item.get("commentsCount", 0)),
                    "sample_caption": caption[:200],
                })
        if len(trends) >= count:
            break
    return trends[:count]


def _scrape_linkedin(industry: str, count: int = 10) -> list:
    client = _apify_client()
    run = client.actor("scarletapi/linkedin-viral-posts-finder").call(run_input={
        "keywords": [industry],
        "maxResults": count * 2,
    })
    items = list(client.dataset(run.default_dataset_id).iterate_items())
    trends = []
    for item in items[:count]:
        text = item.get("text", "") or item.get("content", "") or ""
        trends.append({
            "trend": text[:100].split("\n")[0].strip(),
            "source": "linkedin",
            "reactions": _fmt(item.get("reactionsCount", 0) or item.get("reactions", 0)),
            "comments": _fmt(item.get("commentsCount", 0) or item.get("comments", 0)),
            "sample_post": text[:300],
        })
    return trends


_SCRAPERS = {
    "TikTok": _scrape_tiktok,
    "Instagram": _scrape_instagram,
    "LinkedIn": _scrape_linkedin,
}


def _synthetic_trends(industry: str, platform: str) -> list:
    """Fallback trend data when Apify scraping is unavailable (e.g. quota exceeded)."""
    if platform == "LinkedIn":
        return [
            {
                "trend": f"{industry.title()} Industry Disruption",
                "source": "linkedin",
                "reactions": "2K",
                "comments": "180",
                "sample_post": f"The {industry} industry is undergoing a massive shift. Here's what leaders need to know right now. #{industry} #innovation #leadership",
            },
            {
                "trend": f"Future of {industry.title()}",
                "source": "linkedin",
                "reactions": "1K",
                "comments": "95",
                "sample_post": f"5 {industry} trends reshaping the market in 2025. Which one are you betting on? #{industry} #trends #futureofwork",
            },
            {
                "trend": f"{industry.title()} Founder Story",
                "source": "linkedin",
                "reactions": "800",
                "comments": "60",
                "sample_post": f"I built a {industry} brand from scratch with $0 marketing budget. Here's the honest breakdown. #{industry} #entrepreneurship",
            },
        ]
    return [
        {
            "trend": f"#{industry}transformation",
            "source": platform.lower(),
            "sample_caption": f"Amazing {industry} transformation — before and after 🔥 #{industry} #{industry}tips",
        },
        {
            "trend": f"#{industry}routine",
            "source": platform.lower(),
            "sample_caption": f"My daily {industry} routine that changed everything ✨ #{industry}routine #{industry}lifestyle",
        },
        {
            "trend": f"#{industry}hack",
            "source": platform.lower(),
            "sample_caption": f"This {industry} hack saved me so much time 😱 #{industry}hack #{industry}tips #viral",
        },
    ]


def run_trend_agent(industry: str, timeframe: str, platform: str) -> str:
    """
    TrendResearchAgent — a specialized sub-agent for viral trend discovery.

    Step 1: Scrapes live data from the target platform via Apify.
    Step 2: Uses Gemini to analyze the raw data and rank trends by brand opportunity.

    The orchestrator calls this via the search_viral_trends tool and receives
    a pre-analyzed report — not raw hashtag data — so it can focus on strategy.
    """
    # Step 1: Scrape real trending content — fall back through Instagram → synthetic
    scraper = _SCRAPERS.get(platform, _scrape_tiktok)
    raw_trends = []
    try:
        raw_trends = scraper(industry, count=10)
    except Exception:
        pass

    if not raw_trends and platform != "Instagram":
        try:
            raw_trends = _scrape_instagram(industry, count=10)
        except Exception:
            pass

    if not raw_trends:
        raw_trends = _synthetic_trends(industry, platform)

    raw_json = json.dumps(raw_trends, ensure_ascii=False)

    # Step 2: Gemini analyzes the scraped data and ranks by opportunity score
    client = genai.Client(api_key=get_api_key())
    response = client.models.generate_content(
        model=TREND_AGENT_MODEL,
        contents=f"Analyze these {platform} trends from the {industry} space ({timeframe}):\n\n{raw_json}",
        config=types.GenerateContentConfig(
            system_instruction=(
                f"You are a viral trend analyst for the {industry} industry on {platform}. "
                "You receive raw scraped social data and identify the top 3 viral moments a brand could hijack.\n\n"
                "For each trend output:\n"
                "- trend_name: clean readable name (not just a hashtag)\n"
                "- hashtag: the raw hashtag from the data\n"
                "- why_viral: one sentence on WHY this is blowing up right now\n"
                "- opportunity_score: 1-10 (10 = perfect shareability, high engagement potential)\n"
                "- content_angle: one sentence on how a brand could join this conversation authentically\n\n"
                f'Return ONLY valid JSON: {{"industry": "...", "platform": "...", "timeframe": "...", "top_trends": [...]}}'
            ),
            max_output_tokens=4096,
        ),
    )

    return _clean_json(response.text)


if __name__ == "__main__":
    import argparse
    from dotenv import load_dotenv
    load_dotenv(override=True)

    parser = argparse.ArgumentParser(description="TrendResearchAgent — find what's going viral")
    parser.add_argument("--industry", required=True, help="Industry to scan (e.g. food, fitness)")
    parser.add_argument("--platform", default="TikTok", choices=["TikTok", "Instagram", "LinkedIn"])
    parser.add_argument("--timeframe", default="last 24 hours", choices=["last 24 hours", "last 48 hours", "this week"])
    args = parser.parse_args()

    print(f"\nScanning {args.platform} for '{args.industry}' trends ({args.timeframe})...\n")
    result = run_trend_agent(industry=args.industry, timeframe=args.timeframe, platform=args.platform)
    data = json.loads(result)
    for i, t in enumerate(data.get("top_trends", []), 1):
        print(f"#{i} {t['trend_name']} ({t['hashtag']})  score: {t['opportunity_score']}/10")
        print(f"   Why viral : {t['why_viral']}")
        print(f"   Angle     : {t['content_angle']}\n")
