import sys
import json
import argparse
from pathlib import Path
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule

load_dotenv(override=True)

from src.agent import ViralMomentHijacker  # noqa: E402 — must load .env first

console = Console()


def print_banner():
    console.print(
        Panel(
            "[bold magenta]VIRAL MOMENT HIJACKER[/bold magenta]\n"
            "[dim]AI-powered trend + influencer marketing agent[/dim]",
            border_style="magenta",
            padding=(1, 4),
        )
    )


def display_results(saved_path: str, platform: str):
    console.print()
    console.print(Rule("[bold green]Campaign Complete[/bold green]"))
    console.print(
        f"\n[bold green]✓[/bold green] Saved to [cyan]{saved_path}[/cyan]"
    )

    with open(saved_path, "r", encoding="utf-8") as f:
        campaign = json.load(f)

    console.print()
    console.print(
        Panel(
            f"[bold]{campaign.get('viral_trend', '—')}[/bold]\n\n"
            f"[dim]Brand angle:[/dim] {campaign.get('brand_angle', '—')[:300]}",
            title="[bold magenta]Campaign Summary[/bold magenta]",
            border_style="magenta",
        )
    )

    pitches = campaign.get("influencer_pitches", [])
    if pitches:
        console.print(f"\n[green]✓[/green] {len(pitches)} influencer DM pitch(es) generated")
        for p in pitches:
            handle = p.get("handle") or p.get("name", "Unknown")
            followers = p.get("followers", "—")
            dm = p.get("dm_pitch", "").strip()
            console.print()
            console.print(
                Panel(
                    f"[dim]{handle}  ·  {followers} followers[/dim]\n\n{dm}",
                    title=f"[bold yellow]DM Pitch — {p.get('name', handle)}[/bold yellow]",
                    border_style="yellow",
                )
            )

    brand_post = campaign.get("brand_post", "")
    if brand_post:
        console.print()
        console.print(
            Panel(
                brand_post,
                title=f"[bold]{platform} Post[/bold]",
                border_style="cyan",
            )
        )

    hashtags = campaign.get("hashtag_strategy", {})
    # Gemini may save groups flat or nested under "groups"
    groups = hashtags.get("groups") or hashtags
    if groups.get("broad") or groups.get("niche"):
        console.print()
        formula = hashtags.get("caption_formula", "")
        lines = []
        if groups.get("broad"):
            lines.append(f"[bold]Broad:[/bold]  {' '.join(groups['broad'])}")
        if groups.get("niche"):
            lines.append(f"[bold]Niche:[/bold]  {' '.join(groups['niche'])}")
        if groups.get("branded"):
            lines.append(f"[bold]Brand:[/bold]  {' '.join(groups['branded'])}")
        if groups.get("trend"):
            lines.append(f"[bold]Trend:[/bold]  {' '.join(groups['trend'])}")
        if formula:
            lines.append(f"\n[dim]{formula}[/dim]")
        console.print(Panel(
            "\n".join(lines),
            title="[bold cyan]Hashtag Strategy[/bold cyan]",
            border_style="cyan",
        ))

    calendar = campaign.get("content_calendar", [])
    if calendar:
        console.print()
        cal_lines = []
        for entry in calendar:
            day = entry.get("day", "")
            fmt = entry.get("format", "")
            time = entry.get("optimal_time", "")
            caption = entry.get("caption", "").replace("\n", " ")[:100]
            cal_lines.append(
                f"[bold]{day:<10}[/bold] [yellow]{fmt:<12}[/yellow] "
                f"[dim]{time:<8}[/dim]  {caption}{'…' if len(entry.get('caption','')) > 100 else ''}"
            )
        console.print(Panel(
            "\n".join(cal_lines),
            title="[bold green]7-Day Content Calendar[/bold green]",
            border_style="green",
        ))

    distribution = campaign.get("distribution", {})
    social_url = distribution.get("social_post_url")
    email_subject = distribution.get("customer_email_subject")
    email_subs = distribution.get("customer_email_subscribers")

    if social_url or email_subject:
        console.print()
        console.print("[bold]Distribution[/bold]")
        if social_url:
            console.print(
                f"  [green]✓[/green] Posted to {platform}: [dim cyan]{social_url}[/dim cyan]"
            )
        if email_subject:
            subs_str = f"{email_subs:,} subscribers" if email_subs else "customer list"
            console.print(
                f"  [green]✓[/green] Email sent to {subs_str}: "
                f"[italic]\"{email_subject}\"[/italic]"
            )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Viral Moment Hijacker — AI marketing agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Forkly on TikTok
  python main.py \\
    --industry food \\
    --brand-name "Forkly" \\
    --brand-description "Fun meal kit brand delivering weekly recipe kits to millennials and Gen Z" \\
    --platform TikTok \\
    --tone "casual, witty, food-obsessed"

  # Any brand on Instagram
  python main.py \\
    --industry fitness \\
    --brand-name "ActiveWear Co" \\
    --brand-description "Sustainable activewear for everyday athletes" \\
    --platform Instagram \\
    --tone casual \\
    --brand-values "sustainability, performance, community"
""",
    )
    parser.add_argument(
        "--industry", required=True,
        help="Industry to monitor for trends (e.g., food, fitness, beauty)"
    )
    parser.add_argument(
        "--brand-name", required=True, dest="brand_name",
        help="Your brand name"
    )
    parser.add_argument(
        "--brand-description", required=True, dest="brand_description",
        help="One-sentence brand description"
    )
    parser.add_argument(
        "--platform", required=True,
        choices=["Instagram", "TikTok", "LinkedIn"],
        help="Target social platform"
    )
    parser.add_argument(
        "--tone", default="casual",
        help="Brand tone (e.g., casual, professional, witty). Default: casual"
    )
    parser.add_argument(
        "--brand-values", default="authentic, creative, community-driven",
        dest="brand_values",
        help="Comma-separated brand values. Default: authentic, creative, community-driven"
    )
    parser.add_argument(
        "--find-influencers", action="store_true", dest="find_influencers",
        help="Enable InfluencerAgent: find and score creators, then write personalized DM pitches"
    )
    parser.add_argument(
        "--send-email", action="store_true", dest="send_email",
        help="Enable EmailAgent: write and send a trend-inspired customer email"
    )
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    print_banner()

    console.print("\n[bold]Campaign Configuration[/bold]")
    agents_active = ["TrendResearchAgent"]
    if args.find_influencers:
        agents_active.append("InfluencerAgent")
    if args.send_email:
        agents_active.append("EmailAgent")

    console.print(f"  Brand:    [cyan]{args.brand_name}[/cyan]")
    console.print(f"  Industry: [cyan]{args.industry}[/cyan]")
    console.print(f"  Platform: [cyan]{args.platform}[/cyan]")
    console.print(f"  Tone:     [cyan]{args.tone}[/cyan]")
    console.print(f"  Agents:   [cyan]{', '.join(agents_active)}[/cyan]")
    console.print()
    console.print(Rule("[bold green]Starting Pipeline[/bold green]"))
    console.print()

    try:
        agent = ViralMomentHijacker(
            brand_name=args.brand_name,
            brand_description=args.brand_description,
            tone=args.tone,
            brand_values=args.brand_values,
            console=console,
            use_influencers=args.find_influencers,
            use_email=args.send_email,
        )
        saved_path = agent.run_campaign(industry=args.industry, platform=args.platform)
    except ValueError as e:
        console.print(f"\n[red]Configuration error:[/red] {e}")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[red]Error:[/red] {e}")
        raise

    if saved_path and Path(saved_path).exists():
        display_results(saved_path, args.platform)
    else:
        console.print()
        console.print(Rule("[bold green]Campaign Complete[/bold green]"))
        console.print(
            "\n[yellow]Pipeline finished. Check output/ for any saved results.[/yellow]"
        )


if __name__ == "__main__":
    main()
