from types import SimpleNamespace
from rich.console import Console
from srl.commands import add, list_
from srl.utils import format_problem_link
from srl.storage import load_json, PROGRESS_FILE, NEXT_UP_FILE
import argparse


def add_subparser(subparsers):
    def positive_int(value):
        ivalue = int(value)
        if ivalue < 0:
            raise argparse.ArgumentTypeError(f"{value} is not a positive integer")
        return ivalue

    parser = subparsers.add_parser("take", help="Output a problem by index")
    parser.add_argument(
        "index", type=positive_int, help="Index of the problem to output"
    )
    parser.add_argument(
        "action",
        nargs="?",
        choices=["add"],
        default=None,
        help="Optional action to perform",
    )
    parser.add_argument(
        "rating", type=int, choices=range(1, 6), nargs="?", help="Rating from 1-5"
    )
    parser.set_defaults(handler=handle)
    return parser


def handle(args, console: Console):
    index: int = abs(args.index)
    problem = None
    due_problems = list_.get_due_problems()

    if due_problems and 0 < index <= len(due_problems):
        problem = due_problems[index - 1]

    if not problem:
        return

    if args.action == "add":
        if args.rating is None:
            console.print(
                "[red]Error: rating must be provided when action is 'add'[/red]"
            )
            return
        add.handle(
            SimpleNamespace(identifier=problem, rating=args.rating), console
        )
    else:
        # Load URL for display
        data = load_json(PROGRESS_FILE)
        next_up = load_json(NEXT_UP_FILE)
        url = data.get(problem, {}).get("url") or next_up.get(problem, {}).get("url")
        console.print(format_problem_link(problem, url))
