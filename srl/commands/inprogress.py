from rich.console import Console
from rich.panel import Panel
from srl.utils import format_problem_link
from srl.storage import (
    load_json,
    PROGRESS_FILE,
)


def add_subparser(subparsers):
    parser = subparsers.add_parser("inprogress", help="List problems in progress")
    parser.set_defaults(handler=handle)
    return parser


def handle(args, console: Console):
    in_progress = get_in_progress()
    if in_progress:
        console.print(
            Panel.fit(
                "\n".join(f"{i+1}. {format_problem_link(name, url)}" for i, (name, url) in enumerate(in_progress)),
                title=f"[bold magenta]Problems in Progress ({len(in_progress)})[/bold magenta]",
                border_style="magenta",
                title_align="left",
            )
        )
    else:
        console.print("[yellow]No problems currently in progress.[/yellow]")


def get_in_progress() -> list[tuple[str, str]]:
    data = load_json(PROGRESS_FILE)
    res = []

    for name, info in data.items():
        url = info.get("url")
        res.append((name, url))

    return res
