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

## Mission
Run a viral moment hijacker campaign on {platform} in the {industry} space. Follow these steps in order:

1. **DISCOVER** — Call `search_viral_trends` to find what's going viral in {industry} right now.
2. **IDENTIFY** — Pick the best trend for {self.brand_name}, then call `find_influencers` to find 3 creators actively posting about it on {platform}.
3. **STRATEGIZE** — Choose the brand angle that feels most authentic. If the connection to {self.brand_name} seems forced, pick a different trend.
4. **HASHTAGS** — Call `generate_hashtag_strategy` with 4 groups: broad (1M+ posts), niche (10K–500K posts), branded ({self.brand_name}-owned), and trend-specific hashtags tied to the viral moment. Add a one-line caption formula explaining how to mix them.
5. **PERSONALIZE** — Write a custom DM pitch for each influencer. Reference their specific content. Sound like a real marketing person, not a bot.
6. **CREATE** — Write a reactive brand post for {platform} in {self.brand_name}'s voice. Match the energy and format of the platform.
7. **CALENDAR** — Call `generate_content_calendar` with a 7-day posting plan. Each day: format (use platform-native formats only — for TikTok: Video, Duet, Stitch, Carousel, Story; for Instagram: Reel, Story, Carousel, Feed Post; for LinkedIn: Post, Article, Video), full caption, and optimal posting time. Build momentum — day 1 jumps on the trend, days 2–5 sustain it with related content, days 6–7 convert with a CTA.
8. **POST** — Call `post_to_social_media` to publish the brand post on {self.brand_name}'s {platform} account.
9. **EMAIL** — Write a customer email that connects the viral trend to something actionable for customers. For a meal kit brand, tie the trend to a specific recipe they can select for their next delivery (e.g., "This [trend] recipe is now available — add it to your next kit"). Make the email feel like a friendly heads-up, not a blast. Then call `send_customer_email` to send it.
10. **SAVE** — Call `save_campaign_results` with all generated content, including the `social_post_url` from step 8, the `customer_email_subject` from step 9, the `customer_email_subscribers` count from step 9, the `content_calendar` days array from step 7, and the `hashtag_strategy` object from step 4.

## Quality Rules
- DMs must be warm, specific, and platform-native. No "I came across your profile" openers.
- Brand post must fit {platform}'s native format and tone conventions.
- Customer email subject line must be under 60 characters and make someone want to open it.
- Customer email body should feel personal — reference the trend, make the product recommendation feel timely, end with one clear action.
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
                            block.name, block.input, self.brand_name, platform
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
