import json
import anthropic
from rich.console import Console

from .config import ORCHESTRATOR_MODEL
from .tools import TOOL_SCHEMAS, execute_tool

MAX_ITERATIONS = 15


class ViralMomentHijacker:
    def __init__(
        self,
        brand_name: str,
        brand_description: str,
        tone: str,
        brand_values: str,
        console: Console,
    ):
        self.brand_name = brand_name
        self.brand_description = brand_description
        self.tone = tone
        self.brand_values = brand_values
        self.console = console
        self.client = anthropic.Anthropic()

    def _system_prompt(self, industry: str, platform: str) -> str:
        return f"""You are a viral marketing strategist for {self.brand_name}.

## Brand
- Name: {self.brand_name}
- Description: {self.brand_description}
- Tone: {self.tone}
- Values: {self.brand_values}

## Sub-Agents You Coordinate
You do not work alone. Three specialized AI agents handle the data-heavy and writing tasks:
- **TrendResearchAgent** — called via `search_viral_trends`. Scrapes live {platform} data and returns pre-analyzed trends with opportunity scores and content angles. You pick the best one.
- **InfluencerAgent** — called via `find_influencers`. Evaluates real creator profiles and returns them scored with fit_score and why_good_fit. You use these to write the DM pitches.
- **EmailAgent** — called via `send_customer_email`. Writes the full customer email and simulates sending it. Just provide trend_name, trend_summary, and brand_angle — do NOT write the email yourself.

## Mission
Run a viral moment hijacker campaign on {platform} in the {industry} space. Follow these steps in order:

1. **DISCOVER** — Call `search_viral_trends` to get TrendResearchAgent's analysis of what's going viral in {industry} right now.
2. **IDENTIFY** — Pick the best trend from the agent's report, then call `find_influencers` to get InfluencerAgent's scored creator profiles for that trend on {platform}.
3. **STRATEGIZE** — Choose the brand angle that feels most authentic. If the connection to {self.brand_name} seems forced, pick a different trend.
4. **HASHTAGS** — Call `generate_hashtag_strategy` with 4 groups: broad (1M+ posts), niche (10K–500K posts), branded ({self.brand_name}-owned), and trend-specific hashtags. Add a one-line caption formula.
5. **PERSONALIZE** — Write a custom DM pitch for each influencer using their fit_score, content_style, and recent_trend_post from the InfluencerAgent's report. Sound like a real person, not a bot.
6. **CREATE** — Write a reactive brand post for {platform} in {self.brand_name}'s voice. Match the energy and format of the platform.
7. **CALENDAR** — Call `generate_content_calendar` with a 7-day posting plan. Each day: format (platform-native only — TikTok: Video, Duet, Stitch, Carousel, Story; Instagram: Reel, Story, Carousel, Feed Post; LinkedIn: Post, Article, Video), full caption, and optimal posting time. Day 1 jumps on the trend, days 2–5 sustain, days 6–7 convert with a CTA.
8. **POST** — Call `post_to_social_media` to publish the brand post on {self.brand_name}'s {platform} account.
9. **EMAIL** — Call `send_customer_email` with `trend_name`, `trend_summary`, and `brand_angle`. The EmailAgent writes and sends the email — you do not write the copy.
10. **SAVE** — Call `save_campaign_results` with all content, including the `social_post_url` from step 8, the `customer_email_subject` and `customer_email_subscribers` from the EmailAgent result in step 9, the `content_calendar` days array from step 7, and the `hashtag_strategy` object from step 4.

## Quality Rules
- DMs must be warm, specific, and platform-native. Use the influencer's content_style and recent_trend_post. No "I came across your profile" openers.
- Brand post must fit {platform}'s native format and tone conventions.
- Authenticity over virality — if the angle feels like a stretch, say so.
- Maintain tone throughout: {self.tone}."""

    def run_campaign(self, industry: str, platform: str) -> str | None:
        """Run the full agentic campaign pipeline. Returns the saved file path."""
        system = self._system_prompt(industry, platform)
        messages = [
            {
                "role": "user",
                "content": (
                    f"Launch a viral moment hijacker campaign for {self.brand_name} "
                    f"in the {industry} space on {platform}. "
                    f"Start by discovering what's trending right now."
                ),
            }
        ]

        saved_path = None

        for iteration in range(MAX_ITERATIONS):
            with self.console.status(
                f"[bold green]Claude is reasoning... (step {iteration + 1})[/bold green]",
                spinner="dots",
            ):
                response = self.client.messages.create(
                    model=ORCHESTRATOR_MODEL,
                    max_tokens=8192,
                    thinking={"type": "adaptive"},
                    output_config={"effort": "high"},
                    system=system,
                    tools=TOOL_SCHEMAS,
                    messages=messages,
                )

            # Append full response (includes thinking blocks) to conversation
            messages.append({"role": "assistant", "content": response.content})

            # Print any visible text Claude emitted this turn
            for block in response.content:
                if getattr(block, "type", None) == "text" and block.text.strip():
                    self.console.print(f"\n[white]{block.text}[/white]")

            if response.stop_reason == "end_turn":
                break

            if response.stop_reason == "tool_use":
                tool_results = []

                for block in response.content:
                    if getattr(block, "type", None) != "tool_use":
                        continue

                    self.console.print(
                        f"\n[bold cyan]→ Tool:[/bold cyan] [yellow]{block.name}[/yellow]"
                    )
                    # Show a compact preview of the args (skip large nested arrays)
                    preview = {
                        k: v
                        for k, v in block.input.items()
                        if k != "influencer_pitches"
                    }
                    self.console.print(
                        f"  [dim]{json.dumps(preview, indent=2)[:300]}[/dim]"
                    )

                    with self.console.status(
                        f"  Executing {block.name}...", spinner="line"
                    ):
                        result = execute_tool(
                            block.name,
                            block.input,
                            self.brand_name,
                            platform,
                            brand_description=self.brand_description,
                            tone=self.tone,
                        )

                    # Capture save path so we can display it after the loop
                    if block.name == "save_campaign_results":
                        try:
                            result_data = json.loads(result)
                            saved_path = result_data.get("saved_to")
                        except (json.JSONDecodeError, AttributeError):
                            pass

                    self.console.print(f"  [green]✓ Done[/green]")

                    tool_results.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": result,
                        }
                    )

                messages.append({"role": "user", "content": tool_results})

        return saved_path
