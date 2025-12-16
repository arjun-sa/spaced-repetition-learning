from rich.console import Console
from rich.prompt import Confirm
from srl.storage import (
    load_json,
    save_json,
    PROGRESS_FILE,
    MASTERED_FILE,
    NEXT_UP_FILE,
    AUDIT_FILE,
)


def add_subparser(subparsers):
    parser = subparsers.add_parser(
        "reset",
        help="Reset progress data (with confirmation)"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Reset all data (progress, mastered, next_up, audit)"
    )
    parser.add_argument(
        "--progress",
        action="store_true",
        help="Reset in-progress problems only"
    )
    parser.add_argument(
        "--mastered",
        action="store_true",
        help="Reset mastered problems only"
    )
    parser.add_argument(
        "--next-up",
        action="store_true",
        help="Reset next up queue only"
    )
    parser.add_argument(
        "--audit",
        action="store_true",
        help="Reset audit data only"
    )
    parser.add_argument(
        "-y", "--yes",
        action="store_true",
        help="Skip confirmation prompt"
    )
    parser.set_defaults(handler=handle)
    return parser


def handle(args, console: Console):
    # Determine what to reset
    reset_all = args.all
    reset_progress = args.progress or reset_all
    reset_mastered = args.mastered or reset_all
    reset_next_up = args.next_up or reset_all
    reset_audit = args.audit or reset_all

    # If no flags specified, default to resetting all
    if not (args.progress or args.mastered or args.next_up or args.audit or args.all):
        reset_all = True
        reset_progress = True
        reset_mastered = True
        reset_next_up = True
        reset_audit = True

    # Build confirmation message
    items_to_reset = []
    if reset_progress:
        items_to_reset.append("[cyan]in-progress problems[/cyan]")
    if reset_mastered:
        items_to_reset.append("[cyan]mastered problems[/cyan]")
    if reset_next_up:
        items_to_reset.append("[cyan]next up queue[/cyan]")
    if reset_audit:
        items_to_reset.append("[cyan]audit data[/cyan]")

    if not items_to_reset:
        console.print("[yellow]No data selected to reset.[/yellow]")
        return

    console.print(f"[bold yellow]Warning:[/bold yellow] This will reset: {', '.join(items_to_reset)}")
    console.print("[bold red]This action cannot be undone![/bold red]")

    # Get confirmation unless -y flag is used
    if not args.yes:
        confirmed = Confirm.ask("\nAre you sure you want to continue?", default=False)
        if not confirmed:
            console.print("[yellow]Reset cancelled.[/yellow]")
            return

    # Perform reset
    reset_count = 0

    if reset_progress:
        if PROGRESS_FILE.exists():
            save_json(PROGRESS_FILE, {})
            console.print("[green]✓[/green] Reset in-progress problems")
            reset_count += 1

    if reset_mastered:
        if MASTERED_FILE.exists():
            save_json(MASTERED_FILE, {})
            console.print("[green]✓[/green] Reset mastered problems")
            reset_count += 1

    if reset_next_up:
        if NEXT_UP_FILE.exists():
            save_json(NEXT_UP_FILE, {})
            console.print("[green]✓[/green] Reset next up queue")
            reset_count += 1

    if reset_audit:
        if AUDIT_FILE.exists():
            save_json(AUDIT_FILE, {})
            console.print("[green]✓[/green] Reset audit data")
            reset_count += 1

    if reset_count > 0:
        console.print(f"\n[bold green]Successfully reset {reset_count} data file(s).[/bold green]")
    else:
        console.print("[yellow]No data files found to reset.[/yellow]")
