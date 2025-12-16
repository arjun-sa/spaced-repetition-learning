from rich.console import Console
from srl.utils import resolve_problem_identifier
from srl.storage import (
    load_json,
    save_json,
    PROGRESS_FILE,
)


def add_subparser(subparsers):
    parser = subparsers.add_parser("remove", help="Remove a problem from in-progress")
    parser.add_argument("identifier", type=str, help="Problem name, URL, or number from `srl inprogress`")
    parser.set_defaults(handler=handle)
    return parser


def handle(args, console: Console):
    data = load_json(PROGRESS_FILE)

    # Get list of in-progress problems for number resolution
    in_progress_problems = list(data.keys())

    # Resolve the identifier (URL, number, or name)
    name, _ = resolve_problem_identifier(args.identifier, in_progress_problems, console)

    if not name:
        return  # Error already printed by resolver

    if name in data:
        del data[name]
        save_json(PROGRESS_FILE, data)
        console.print(
            f"[green]Removed[/green] '[cyan]{name}[/cyan]' [green]from in-progress.[/green]"
        )
    else:
        console.print(
            f"[red]Problem[/red] '[cyan]{name}[/cyan]' [red]not found in in-progress.[/red]"
        )
