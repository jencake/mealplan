"""CLI entry point for mealplan."""

import argparse
import os
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

import pytz
from calparse import fetch_ics, parse_ics
from dotenv import load_dotenv

from .schedule import get_meals_for_day, Meal, is_iron_day, find_iron_slot, parse_time
from .formatter import format_schedule, CalendarEvent
from .rule_engine import MinSpacingRule, MaxTimeRule, SkipLateSnackRule, apply_rules


OVERRIDES_DIR = Path.home() / ".config" / "mealplan" / "overrides"
CACHE_DIR = Path.home() / ".cache" / "mealplan"
CACHE_TTL_SECONDS = 28800  # 8 hours

# Valid meal names for logging
VALID_MEALS = {
    "breakfast": "Breakfast",
    "morning-snack": "Morning Snack",
    "lunch": "Lunch",
    "afternoon-snack": "Afternoon Snack",
    "dinner": "Dinner",
    "evening-snack": "Evening Snack",
    "iron": "Iron Supplement",
}

DEFAULT_RULES = [
    MinSpacingRule(2),
    MaxTimeRule("Dinner", "8:30pm"),
    SkipLateSnackRule(after_hour=19),
]

def parse_date_arg(arg: str) -> date:
    """Parse date argument: today, tomorrow, or YYYY-MM-DD."""
    arg = arg.lower().strip()
    today = date.today()

    if arg == "today":
        return today
    elif arg == "tomorrow":
        return today + timedelta(days=1)

    weekdays = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    if arg in weekdays:
        target_weekday = weekdays.index(arg)
        current_weekday = today.weekday()
        delta = target_weekday - current_weekday
        return today + timedelta(days=delta)

    try:
        return datetime.strptime(arg, "%Y-%m-%d").date()
    except ValueError:
        print(f"Error: Invalid date format '{arg}'. Use YYYY-MM-DD.", file=sys.stderr)
        sys.exit(1)


def load_overrides(target_date: date) -> dict[str, str]:
    """Load override file for a specific date if it exists.

    Override file format (markdown table):
    | Meal | Time | Override |
    |------|------|----------|
    | Lunch | 1:00pm | Eating out at Local Deli |
    """
    override_file = OVERRIDES_DIR / f"{target_date.isoformat()}.md"
    if not override_file.exists():
        return {}

    overrides = {}
    try:
        content = override_file.read_text()
        lines = content.strip().split("\n")

        # Find the table: look for header row with "| Meal |"
        in_table = False
        skip_separator = False
        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Detect table header
            if line.startswith("|") and "meal" in line.lower():
                in_table = True
                skip_separator = True
                continue

            # Skip separator row (|------|------|)
            if skip_separator and line.startswith("|") and "---" in line:
                skip_separator = False
                continue

            # Parse data rows
            if in_table and line.startswith("|"):
                parts = [p.strip() for p in line.split("|")]
                if len(parts) >= 4:
                    meal = parts[1]
                    time_str = parts[2]
                    override_desc = parts[3]
                    if meal and override_desc:
                        overrides[meal.lower()] = (time_str, override_desc)
    except Exception as e:
        print(f"Warning: Could not parse override file: {e}", file=sys.stderr)

    return overrides


def save_override(target_date: date, meal_name: str, description: str, time_str: str = "") -> None:
    """Save or update an override entry for a meal."""
    OVERRIDES_DIR.mkdir(parents=True, exist_ok=True)
    override_file = OVERRIDES_DIR / f"{target_date.isoformat()}.md"

    # Load existing overrides
    existing = {}
    if override_file.exists():
        content = override_file.read_text()
        lines = content.strip().split("\n")
        in_table = False
        for line in lines:
            line = line.strip()
            if line.startswith("|") and "meal" in line.lower():
                in_table = True
                continue
            if in_table and line.startswith("|") and "---" not in line:
                parts = [p.strip() for p in line.split("|")]
                if len(parts) >= 4 and parts[1]:
                    existing[parts[1]] = (parts[2], parts[3])

    # Update with new entry
    existing[meal_name] = (time_str, description)

    # Write back
    lines = [
        "| Meal | Time | Override |",
        "|------|------|----------|",
    ]
    for meal, (t, desc) in existing.items():
        lines.append(f"| {meal} | {t} | {desc} |")

    override_file.write_text("\n".join(lines) + "\n")


def get_cached_ics(url: str) -> str:
    """Fetch ICS content with file-based caching."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_file = CACHE_DIR / "calendar.ics"

    # Check if cache is fresh
    if cache_file.exists():
        age = datetime.now().timestamp() - cache_file.stat().st_mtime
        if age < CACHE_TTL_SECONDS:
            return cache_file.read_text()

    # Fetch fresh and update cache
    content = fetch_ics(url)
    cache_file.write_text(content)
    return content


def fetch_calendar_events(target_date: date) -> list[CalendarEvent]:
    """Fetch calendar events for the target date using calparse."""
    ics_url = os.environ.get("OUTLOOK_CALENDAR_ICS")
    if not ics_url:
        return []

    try:
        ics_content = get_cached_ics(ics_url)
        local_tz = pytz.timezone("America/Los_Angeles")
        events = parse_ics(ics_content, target_date, target_date, local_tz)

        return [
            CalendarEvent(
                summary=e.summary,
                start=e.start,
                end=e.end,
                is_all_day=e.is_all_day,
            )
            for e in events
        ]
    except Exception:
        return []


def cmd_show(args):
    """Show the meal schedule for a date."""
    target_date = parse_date_arg(args.date)
    day_name = target_date.strftime("%A")

    # Get base meals for this day
    meals = get_meals_for_day(day_name)

    # Load any overrides
    overrides = load_overrides(target_date)
    if overrides:
        # Apply overrides to meals
        updated_meals = []
        for meal in meals:
            key = meal.name.lower()
            if key in overrides:
                time_str, desc = overrides[key]
                updated_meals.append(Meal(
                    time=time_str if time_str else meal.time,
                    name=meal.name,
                    description=desc,
                    notes=meal.notes,
                ))
            else:
                updated_meals.append(meal)
        meals = updated_meals

    # Now apply rules — sees the actual logged times
    meals = apply_rules(meals, DEFAULT_RULES, target_date)

    # Fetch calendar events
    events = None
    if not args.no_calendar:
        events = fetch_calendar_events(target_date)

    # Add iron supplement if it's an iron day
    if is_iron_day(target_date, OVERRIDES_DIR):
        iron_time = find_iron_slot(meals, events or [], target_date)
        if iron_time:
            # Found a free slot - add iron as standalone
            meals.append(Meal(iron_time, "Iron Supplement", "🩸 Take on empty stomach"))
            meals.sort(key=lambda m: parse_time(m.time))
        else:
            # No free slot - take iron with evening snack using iron-friendly food
            # Replace evening snack with iron-friendly version (no dairy, high vitamin C)
            meals = [
                Meal(
                    time=m.time,
                    name=m.name,
                    description="🩸 Iron + 1 orange + handful berries (vitamin C aids absorption)"
                    if m.name == "Evening Snack" else m.description,
                    notes=m.notes,
                )
                for m in meals
            ]

    # Format and print
    output = format_schedule(target_date, meals, events)
    print(output)


def cmd_log(args):
    """Log what was actually eaten for a meal."""
    meal_key = args.meal.lower()
    if meal_key not in VALID_MEALS:
        print(f"Error: Unknown meal '{args.meal}'", file=sys.stderr)
        print(f"Valid meals: {', '.join(VALID_MEALS.keys())}", file=sys.stderr)
        sys.exit(1)

    meal_name = VALID_MEALS[meal_key]
    target_date = parse_date_arg(args.date)
    time_str = args.time or ""

    save_override(target_date, meal_name, args.description, time_str)
    print(f"Logged {meal_name} for {target_date}: {args.description}")


def main():
    """Main CLI entry point."""
    # Load .env from project root
    env_path = Path(__file__).parent.parent / ".env"
    load_dotenv(env_path)

    # Handle backward compatibility: if first arg isn't a subcommand, treat as date
    if len(sys.argv) > 1 and sys.argv[1] not in ["show", "log", "-h", "--help"]:
        # Insert "show" as the subcommand
        sys.argv.insert(1, "show")

    parser = argparse.ArgumentParser(
        prog="mealplan",
        description="Meal schedule CLI with optional pregnancy tracking"
    )
    subparsers = parser.add_subparsers(dest="command")

    # Show command (default)
    show_parser = subparsers.add_parser("show", help="Show meal schedule")
    show_parser.add_argument(
        "date",
        nargs="?",
        default="today",
        help="Date: today, tomorrow, weekday, or YYYY-MM-DD (default: today)"
    )
    show_parser.add_argument(
        "--no-calendar",
        action="store_true",
        help="Skip calendar conflict detection"
    )

    # Log command
    log_parser = subparsers.add_parser("log", help="Log what was eaten")
    log_parser.add_argument(
        "meal",
        choices=list(VALID_MEALS.keys()),
        help="Meal to log"
    )
    log_parser.add_argument(
        "description",
        help="What was eaten"
    )
    log_parser.add_argument(
        "--time", "-t",
        help="Time eaten (e.g., 1:30pm)"
    )
    log_parser.add_argument(
        "--date", "-d",
        default="today",
        help="Date to log for (default: today)"
    )

    args = parser.parse_args()

    # Default to show if no command
    if args.command is None:
        args.command = "show"
        args.date = "today"
        args.no_calendar = False

    if args.command == "show":
        cmd_show(args)
    elif args.command == "log":
        cmd_log(args)


if __name__ == "__main__":
    main()
