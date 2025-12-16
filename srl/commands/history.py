from rich.console import Console
from rich.table import Table
from srl.utils import format_problem_link
from srl.storage import (
    load_json,
    PROGRESS_FILE,
    MASTERED_FILE,
)
from datetime import datetime


def add_subparser(subparsers):
    parser = subparsers.add_parser("history", help="Show recent activity history")
    parser.add_argument(
        "-n",
        type=int,
        default=20,
        help="Number of recent entries to show (default: 20)"
    )
    parser.set_defaults(handler=handle)
    return parser


def handle(args, console: Console):
    limit = args.n if hasattr(args, "n") else 20
    history_entries = get_history(limit)

    if not history_entries:
        console.print("[yellow]No history found.[/yellow]")
        return

    table = Table(
        title=f"Recent Activity (Last {len(history_entries)} entries)",
        title_justify="left"
    )
    table.add_column("Date", style="green")
    table.add_column("Problem", style="cyan")
    table.add_column("Rating", style="yellow", justify="center")
    table.add_column("Status", style="magenta")

    for entry in history_entries:
        date_str = entry["date"]
        problem_name = entry["problem"]
        rating = entry["rating"]
        status = entry["status"]
        url = entry["url"]

        # Format rating with stars
        rating_display = "★" * rating + "☆" * (5 - rating)

        table.add_row(
            date_str,
            format_problem_link(problem_name, url),
            f"{rating} {rating_display}",
            status
        )

    console.print(table)


def get_history(limit: int = 20) -> list[dict]:
    """
    Get recent history entries from all problems.
    Returns a list of dicts with keys: date, problem, rating, status, url
    """
    progress = load_json(PROGRESS_FILE)
    mastered = load_json(MASTERED_FILE)

    entries = []
    index = 0

    # Collect entries from progress
    for name, info in progress.items():
        url = info.get("url")
        for attempt in info.get("history", []):
            entries.append({
                "date": attempt["date"],
                "problem": name,
                "rating": attempt["rating"],
                "status": "In Progress",
                "url": url,
                "datetime": datetime.fromisoformat(attempt["date"]),
                "index": index
            })
            index += 1

    # Collect entries from mastered
    for name, info in mastered.items():
        url = info.get("url")
        for attempt in info.get("history", []):
            entries.append({
                "date": attempt["date"],
                "problem": name,
                "rating": attempt["rating"],
                "status": "Mastered",
                "url": url,
                "datetime": datetime.fromisoformat(attempt["date"]),
                "index": index
            })
            index += 1

    # Sort by date (most recent first), then by index (later entries first for same date)
    entries.sort(key=lambda x: (x["datetime"], x["index"]), reverse=True)

    # Remove the datetime and index fields (used only for sorting)
    for entry in entries:
        del entry["datetime"]
        del entry["index"]

    # Return limited results
    return entries[:limit]
