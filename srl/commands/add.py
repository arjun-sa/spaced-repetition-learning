from rich.console import Console
from srl.utils import today, resolve_problem_identifier
from srl.storage import (
    load_json,
    save_json,
    PROGRESS_FILE,
    MASTERED_FILE,
    NEXT_UP_FILE,
)
from srl.commands.list_ import get_due_problems


def add_subparser(subparsers):
    add = subparsers.add_parser("add", help="Add or update a problem attempt")
    add.add_argument("identifier", type=str, help="Problem name, URL, or number from `srl list`")
    add.add_argument("rating", type=int, choices=range(1, 6), help="Rating from 1-5")
    add.set_defaults(handler=handle)
    return add


def handle(args, console: Console):
    rating: int = args.rating

    # Get list of due problems for number resolution
    problems = get_due_problems()

    # Resolve the identifier (URL, number, or name)
    name, url = resolve_problem_identifier(args.identifier, problems, console)

    if not name:
        return  # Error already printed by resolver

    data = load_json(PROGRESS_FILE)

    # Check for existing entry case-insensitively
    existing_name = None
    for key in data:
        if key.lower() == name.lower():
            existing_name = key
            break

    # Use existing name if found, otherwise use the provided name
    target_name = existing_name if existing_name else name
    entry = data.get(target_name, {"history": []})

    # Store URL if provided and not already stored
    if url and "url" not in entry:
        entry["url"] = url

    entry["history"].append(
        {
            "rating": rating,
            "date": today().isoformat(),
        }
    )

    # Mastery check: last two ratings are 5
    history = entry["history"]
    if len(history) >= 2 and history[-1]["rating"] == 5 and history[-2]["rating"] == 5:
        mastered = load_json(MASTERED_FILE)
        if target_name in mastered:
            mastered[target_name]["history"].extend(history)
        else:
            mastered[target_name] = entry
        save_json(MASTERED_FILE, mastered)
        if target_name in data:
            del data[target_name]
        console.print(
            f"[bold green]{target_name}[/bold green] moved to [cyan]mastered[/cyan]!"
        )
    else:
        data[target_name] = entry
        console.print(
            f"Added rating [yellow]{rating}[/yellow] for '[cyan]{target_name}[/cyan]'"
        )

    save_json(PROGRESS_FILE, data)

    # Remove from next up if it exists there
    next_up = load_json(NEXT_UP_FILE)
    if target_name in next_up:
        del next_up[target_name]
        save_json(NEXT_UP_FILE, next_up)
