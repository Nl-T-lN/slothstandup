import sys
import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown

from .git_collector import GitCollector
from .gemma_engine import GemmaEngine
from .formatter import StandupFormatter

console = Console()

SLOTH_BANNER = r"""[bold green]
   (\_/)  
   ( •.•)  [yellow]SlothStandup 🦥[/yellow]
   / >🌱  [dim]v0.1.0 • Powered by Gemma (Open-Weight)[/dim]
[/bold green]"""


@click.command()
@click.option("--repo", "-r", default=".", help="Path to the local git repository (default: current dir).")
@click.option("--since", "-s", default="yesterday", help="Timeframe for git log (default: 'yesterday', or '2 days ago', '7 days ago').")
@click.option("--author", "-a", default=None, help="Filter git commits by author name or email.")
@click.option("--format", "-f", "output_format", type=click.Choice(["all", "slack", "markdown", "timesheet"]), default="all", help="Output display format.")
@click.option("--model", "-m", default="gemma2:2b", help="Target open-weight Gemma model identifier (default: 'gemma2:2b').")
def main(repo: str, since: str, author: str, output_format: str, model: str):
    """🦥 SlothStandup: Generate daily standups and timesheets from git activity using Gemma."""
    console.print(SLOTH_BANNER)

    with console.status("[bold cyan]Crawling git logs and consulting Gemma...[/bold cyan]", spinner="dots"):
        collector = GitCollector(repo_path=repo)
        activity = collector.collect(since=since, author=author)

        engine = GemmaEngine(model=model)
        result = engine.generate(activity)

    console.print(f"[bold green]✔[/bold green] [bold white]Analysis complete for branch[/bold white] [magenta]'{activity.branch}'[/magenta] [dim]({activity.stats.get('insertions', 0)} + / {activity.stats.get('deletions', 0)} - across {activity.stats.get('files', 0)} files)[/dim]\n")

    # Render Slack View
    if output_format in ("all", "slack"):
        slack_text = StandupFormatter.to_slack(result)
        console.print(Panel(
            slack_text,
            title="[bold blue]💬 Slack / Teams Ready[/bold blue]",
            subtitle="[dim]Copy & paste directly into your standup channel[/dim]",
            border_style="blue"
        ))

    # Render Timesheet View
    if output_format in ("all", "timesheet"):
        timesheet_table = Table(title="⏱️ Automated Timesheet Breakdown", show_header=True, header_style="bold magenta")
        timesheet_table.add_column("Category", style="cyan", width=22)
        timesheet_table.add_column("Task Description", style="white")
        timesheet_table.add_column("Logged Hours", justify="right", style="green")

        total_hrs = 0.0
        for entry in result.get("timesheet", []):
            hrs = float(entry.get("hours", 0.0))
            total_hrs += hrs
            timesheet_table.add_row(entry.get("category", "General"), entry.get("task", ""), f"{hrs:.1f}h")

        timesheet_table.add_section()
        timesheet_table.add_row("[bold]Total Hours[/bold]", "[dim]Auto-reconciled[/dim]", f"[bold green]{total_hrs:.1f}h[/bold green]")
        console.print(timesheet_table)

    # Render Markdown / Sloth Score
    if output_format in ("all", "markdown"):
        laziness = result.get("laziness_score", 95)
        quote = result.get("sloth_quote", "Stay rested.")
        
        info_panel = f"""[bold yellow]Sloth Wisdom:[/bold yellow] [italic]{quote}[/italic]
[bold green]Laziness Quotient:[/bold green] [bold]{laziness}%[/bold] [dim](Effort saved: ~45 mins of manual status reporting)[/dim]
[bold cyan]Architecture:[/bold cyan] [dim]Local Gemma open weights • 100% private on-device • $0 API cost[/dim]"""
        
        console.print(Panel(
            info_panel,
            title="[bold green]🦥 Sloth Efficiency Report[/bold green]",
            border_style="green"
        ))

    console.print("\n[dim green]Now close your laptop and take a nap. You've earned it.[/dim green]\n")


if __name__ == "__main__":
    main()
