from datetime import datetime
import re
from typing import Optional
from rich.console import Console


def today():
    return datetime.today().date()


def extract_problem_name_from_url(url: str) -> Optional[str]:
    """
    Extract problem name from a LeetCode URL.
    Example: https://leetcode.com/problems/two-sum/description/ -> "Two Sum"
    """
    match = re.search(r'leetcode\.com/problems/([^/]+)', url)
    if match:
        slug = match.group(1)
        # Convert slug to title case: "two-sum" -> "Two Sum"
        return ' '.join(word.capitalize() for word in slug.split('-'))
    return None


def problem_name_to_url(name: str) -> str:
    """
    Convert a problem name to a LeetCode URL.
    Example: "Two Sum" -> "https://leetcode.com/problems/two-sum/description/"
    """
    # Convert to lowercase and replace spaces with hyphens
    slug = name.lower().replace(' ', '-')
    return f"https://leetcode.com/problems/{slug}/description/"


def format_problem_link(name: str, url: Optional[str] = None) -> str:
    """
    Format a problem name as a clickable Rich console link if URL is provided.
    Example: format_problem_link("Two Sum", "https://...") -> "[link=https://...]Two Sum[/link]"
    If no URL is provided, returns the plain name.
    """
    if url:
        return f"[link={url}]{name}[/link]"
    return name


def resolve_problem_identifier(
    identifier: str,
    problem_list: list[str],
    console: Console
) -> tuple[Optional[str], Optional[str]]:
    """
    Resolve a problem identifier that could be:
    - A LeetCode URL
    - A problem number (as string)
    - A problem name

    Returns a tuple of (problem_name, url). URL is None if not provided.
    """
    # Check if it's a URL
    if identifier.startswith('http://') or identifier.startswith('https://'):
        problem_name = extract_problem_name_from_url(identifier)
        if problem_name:
            return (problem_name, identifier)
        else:
            console.print(f"[red]Could not extract problem name from URL:[/red] {identifier}")
            return (None, None)

    # Check if it's a number
    if identifier.isdigit():
        num = int(identifier)
        if 1 <= num <= len(problem_list):
            return (problem_list[num - 1], None)
        else:
            console.print(f"[red]Invalid problem number:[/red] {num}")
            return (None, None)

    # Otherwise, treat it as a problem name
    return (identifier, None)
