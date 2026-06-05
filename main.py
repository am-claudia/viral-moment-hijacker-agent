import sys
import json
import argparse
from pathlib import Path
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule

load_dotenv()

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
    console.print(f"\n[green]✓[/green] {len(pitches)} DM pitch(es) generated")
    for p in pitches:
        handle = p.get("handle") or p.get("name", "Unknown")
        followers = p.get("followers", "—")
        console.print(f"  → [cyan]{handle}[/cyan]  ({followers} followers)")

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
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    print_banner()

    console.print("\n[bold]Campaign Configuration[/bold]")
    console.print(f"  Brand:    [cyan]{args.brand_name}[/cyan]")
    console.print(f"  Industry: [cyan]{args.industry}[/cyan]")
    console.print(f"  Platform: [cyan]{args.platform}[/cyan]")
    console.print(f"  Tone:     [cyan]{args.tone}[/cyan]")
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
