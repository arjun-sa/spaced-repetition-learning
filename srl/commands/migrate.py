from rich.console import Console
from srl.utils import extract_problem_name_from_url
from srl.storage import (
    load_json,
    save_json,
    PROGRESS_FILE,
    MASTERED_FILE,
    NEXT_UP_FILE,
)


def add_subparser(subparsers):
    parser = subparsers.add_parser(
        "migrate",
        help="Migrate URL entries to problem names (merge duplicates)"
    )
    parser.set_defaults(handler=handle)
    return parser


def migrate_file(file_path, console: Console) -> tuple[int, int]:
    """
    Migrate URL entries in a file to problem names.
    Returns (merged_count, renamed_count)
    """
    data = load_json(file_path)
    if not data:
        return 0, 0

    merged_count = 0
    renamed_count = 0
    urls_to_remove = []

    # Find all URL entries (convert to list to avoid modification during iteration)
    for key in list(data.keys()):
        if key.startswith('http://') or key.startswith('https://'):
            problem_name = extract_problem_name_from_url(key)

            if not problem_name:
                console.print(f"[yellow]Warning:[/yellow] Could not extract name from {key}")
                continue

            # Check if there's already an entry with the problem name
            existing_entry = None
            for existing_key in data.keys():
                if existing_key.lower() == problem_name.lower() and existing_key != key:
                    existing_entry = existing_key
                    break

            if existing_entry:
                # Merge histories
                url_history = data[key].get("history", [])
                data[existing_entry]["history"].extend(url_history)

                # Sort by date
                data[existing_entry]["history"].sort(key=lambda x: x.get("date", ""))

                urls_to_remove.append(key)
                merged_count += 1
                console.print(f"[green]Merged[/green] '{key}' into '{existing_entry}'")
            else:
                # No existing entry, rename the URL entry to the problem name
                data[problem_name] = data[key]
                urls_to_remove.append(key)
                renamed_count += 1
                console.print(f"[blue]Renamed[/blue] '{key}' to '{problem_name}'")

    # Remove URL entries
    for url in urls_to_remove:
        del data[url]

    # Save if changes were made
    if merged_count > 0 or renamed_count > 0:
        save_json(file_path, data)

    return merged_count, renamed_count


def handle(args, console: Console):
    console.print("[bold]Starting migration...[/bold]\n")

    total_merged = 0
    total_renamed = 0

    # Migrate progress file
    console.print("[cyan]Checking problems_in_progress.json...[/cyan]")
    merged, renamed = migrate_file(PROGRESS_FILE, console)
    total_merged += merged
    total_renamed += renamed

    # Migrate mastered file
    console.print("\n[cyan]Checking problems_mastered.json...[/cyan]")
    merged, renamed = migrate_file(MASTERED_FILE, console)
    total_merged += merged
    total_renamed += renamed

    # Migrate next up file
    console.print("\n[cyan]Checking next_up.json...[/cyan]")
    merged, renamed = migrate_file(NEXT_UP_FILE, console)
    total_merged += merged
    total_renamed += renamed

    # Summary
    console.print(f"\n[bold green]Migration complete![/bold green]")
    console.print(f"  Merged: {total_merged}")
    console.print(f"  Renamed: {total_renamed}")
    console.print(f"  Total changes: {total_merged + total_renamed}")
