import json
from google import genai
from google.genai import types
from rich.console import Console

from .config import ORCHESTRATOR_MODEL, get_api_key
from .tools import TOOL_SCHEMAS, execute_tool

MAX_ITERATIONS = 15


def _build_tools(use_influencers: bool, use_email: bool) -> list[types.Tool]:
    """Build Gemini FunctionDeclarations for the active pipeline steps."""
    enabled = {"search_viral_trends", "save_campaign_results"}
    if use_influencers:
        enabled.add("find_influencers")
    if use_email:
        enabled.add("send_customer_email")

    declarations = [
        types.FunctionDeclaration(
            name=schema["name"],
            description=schema["description"],
            parameters=schema["input_schema"],
        )
        for schema in TOOL_SCHEMAS
        if schema["name"] in enabled
    ]
    return [types.Tool(function_declarations=declarations)]


class ViralMomentHijacker:
    def __init__(
        self,
        brand_name: str,
        brand_description: str,
        tone: str,
        brand_values: str,
        console: Console,
        use_influencers: bool = False,
        use_email: bool = False,
    ):
        self.brand_name = brand_name
        self.brand_description = brand_description
        self.tone = tone
        self.brand_values = brand_values
        self.console = console
        self.use_influencers = use_influencers
        self.use_email = use_email
        self.client = genai.Client(api_key=get_api_key())
        self._tools = _build_tools(use_influencers, use_email)

    def _system_prompt(self, industry: str, platform: str) -> str:
        # Build sub-agent directory based on active agents
        sub_agents = (
            "- **TrendResearchAgent** — called via `search_viral_trends`. "
            f"Scrapes live {platform} data and returns pre-analyzed trends with opportunity scores and content angles. You pick the best one."
        )
        if self.use_influencers:
            sub_agents += (
                "\n- **InfluencerAgent** — called via `find_influencers`. "
                "Evaluates real creator profiles and returns them scored with fit_score and why_good_fit. You use these to write the DM pitches."
            )
        if self.use_email:
            sub_agents += (
                "\n- **EmailAgent** — called via `send_customer_email`. "
                "Writes the full customer email and simulates sending it. Just provide trend_name, trend_summary, and brand_angle — do NOT write the email yourself."
            )

        # Build numbered mission steps based on active agents
        n = 1
        steps = [
            f"{n}. **DISCOVER** — Call `search_viral_trends` to get TrendResearchAgent's analysis of what's going viral in {industry} right now."
        ]
        n += 1

        if self.use_influencers:
            steps.append(
                f"{n}. **IDENTIFY** — Pick the best trend from the report, then call `find_influencers` to get InfluencerAgent's scored creator profiles for that trend on {platform}."
            )
            n += 1

        steps.append(
            f"{n}. **STRATEGIZE** — Choose the brand angle that feels most authentic. If the connection to {self.brand_name} seems forced, pick a different trend."
        )
        n += 1

        if self.use_influencers:
            steps.append(
                f"{n}. **PERSONALIZE** — Write a custom DM pitch for each influencer using their fit_score, content_style, and recent_trend_post. Sound like a real person, not a bot."
            )
            n += 1

        if self.use_email:
            steps.append(
                f"{n}. **EMAIL** — Call `send_customer_email` with `trend_name`, `trend_summary`, and `brand_angle`. The EmailAgent writes and sends the email — you do not write the copy."
            )
            n += 1

        # Build save instruction based on what was collected
        save_fields = ["viral_trend", "trend_summary", "brand_angle", "platform"]
        if self.use_influencers:
            save_fields.append("influencer_pitches")
        if self.use_email:
            save_fields.extend(["customer_email_subject", "customer_email_subscribers"])
        steps.append(
            f"{n}. **SAVE** — Call `save_campaign_results` with: {', '.join(save_fields)}."
        )

        return f"""You are a viral marketing strategist for {self.brand_name}.

## Brand
- Name: {self.brand_name}
- Description: {self.brand_description}
- Tone: {self.tone}
- Values: {self.brand_values}

## Sub-Agents You Coordinate
{sub_agents}

## Mission
Run a campaign on {platform} in the {industry} space. Follow these steps in order:

{chr(10).join(steps)}

## Quality Rules
- Authenticity over virality — if the brand angle feels forced, pick a different trend.
- Maintain tone throughout: {self.tone}.
{('- DMs must be warm and specific. Use the influencer content_style and recent_trend_post. No generic openers.' if self.use_influencers else '')}"""

    def run_campaign(self, industry: str, platform: str) -> str | None:
        """Run the full agentic campaign pipeline. Returns the saved file path."""
        system = self._system_prompt(industry, platform)
        messages: list[types.Content] = [
            types.Content(
                role="user",
                parts=[types.Part(text=(
                    f"Launch a viral moment hijacker campaign for {self.brand_name} "
                    f"in the {industry} space on {platform}. "
                    f"Start by discovering what's trending right now."
                ))],
            )
        ]

        saved_path = None

        for iteration in range(MAX_ITERATIONS):
            with self.console.status(
                f"[bold green]Gemini is reasoning... (step {iteration + 1})[/bold green]",
                spinner="dots",
            ):
                response = self.client.models.generate_content(
                    model=ORCHESTRATOR_MODEL,
                    contents=messages,
                    config=types.GenerateContentConfig(
                        system_instruction=system,
                        tools=self._tools,
                        max_output_tokens=8192,
                    ),
                )

            model_content = response.candidates[0].content
            messages.append(model_content)

            # Print any visible text Gemini emitted this turn
            for part in model_content.parts:
                if part.text and part.text.strip():
                    self.console.print(f"\n[white]{part.text}[/white]")

            # Collect function calls from this turn
            tool_calls = [p for p in model_content.parts if p.function_call]

            if not tool_calls:
                break

            function_response_parts = []

            for part in tool_calls:
                fc = part.function_call
                tool_name = fc.name
                # JSON round-trip ensures plain Python types for all nested values
                tool_args = json.loads(json.dumps(dict(fc.args)))

                self.console.print(
                    f"\n[bold cyan]→ Tool:[/bold cyan] [yellow]{tool_name}[/yellow]"
                )
                preview = {k: v for k, v in tool_args.items() if k != "influencer_pitches"}
                self.console.print(
                    f"  [dim]{json.dumps(preview, indent=2)[:300]}[/dim]"
                )

                with self.console.status(
                    f"  Executing {tool_name}...", spinner="line"
                ):
                    result = execute_tool(
                        tool_name,
                        tool_args,
                        self.brand_name,
                        platform,
                        brand_description=self.brand_description,
                        tone=self.tone,
                    )

                if tool_name == "save_campaign_results":
                    try:
                        result_data = json.loads(result)
                        saved_path = result_data.get("saved_to")
                    except (json.JSONDecodeError, AttributeError):
                        pass

                self.console.print(f"  [green]✓ Done[/green]")

                try:
                    response_payload = json.loads(result)
                except (json.JSONDecodeError, TypeError):
                    response_payload = {"result": result}

                function_response_parts.append(
                    types.Part(
                        function_response=types.FunctionResponse(
                            name=tool_name,
                            response=response_payload,
                        )
                    )
                )

            messages.append(types.Content(role="user", parts=function_response_parts))

        return saved_path
