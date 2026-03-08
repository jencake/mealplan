"""Output formatting for meal schedule."""

from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional

from .schedule import Meal, parse_time
from .config import PREGNANCY_ENABLED
from .pregnancy import calculate_week, get_weekly_tip


def times_overlap(meal_time: str, event_start: datetime, event_end: datetime) -> bool:
    """Check if a meal time overlaps with a calendar event."""
    meal_t = parse_time(meal_time)
    event_start_t = event_start.time()
    event_end_t = event_end.time()

    # Simple overlap check - meal time falls within event window
    return event_start_t <= meal_t <= event_end_t


def is_meal_event(event_summary: str) -> bool:
    """Check if a calendar event is likely a meal (restaurant, lunch with, etc.)."""
    summary_lower = event_summary.lower()
    meal_keywords = [
        "lunch", "dinner", "breakfast", "brunch",
        "restaurant", "cafe", "coffee",
        "deli", "grill", "kitchen", "bistro",
        "eating", "food",
    ]
    return any(kw in summary_lower for kw in meal_keywords)


@dataclass
class CalendarEvent:
    """Simple calendar event for conflict detection."""
    summary: str
    start: datetime
    end: datetime
    is_all_day: bool = False


def format_schedule(
    target_date: date,
    meals: list[Meal],
    events: Optional[list[CalendarEvent]] = None,
) -> str:
    """Format the meal schedule with optional calendar conflict detection."""
    day_name = target_date.strftime("%A")
    date_str = target_date.strftime("%B %-d, %Y")

    lines = []
    lines.append(f"## Meals for {day_name}, {date_str}")
    lines.append("")

    # Header
    lines.append("Time      Meal                    Suggestion")
    lines.append("─" * 70)

    conflicts = []
    meal_events = []

    for meal in meals:
        # Skip empty bedtime description
        if meal.name == "Bedtime":
            lines.append(f"{meal.time:<9} {meal.name:<23}")
            continue

        # Check for calendar conflicts
        conflict_event = None
        if events:
            for event in events:
                if event.is_all_day:
                    continue
                if times_overlap(meal.time, event.start, event.end):
                    if is_meal_event(event.summary):
                        meal_events.append((meal.time, event.summary))
                    else:
                        conflict_event = event
                    break

        # Format meal line
        name_with_notes = meal.name
        if meal.notes:
            name_with_notes = f"{meal.name} ({meal.notes})"

        lines.append(f"{meal.time:<9} {name_with_notes:<23} {meal.description}")

        if conflict_event:
            conflicts.append((meal.time, conflict_event.summary))

    lines.append("")

    # Show conflicts
    for time_str, event_name in conflicts:
        lines.append(f"⚠️ {time_str} conflict: \"{event_name}\" → adjust meal time")

    # Show meal events
    for time_str, event_name in meal_events:
        lines.append(f"✓ {time_str}: \"{event_name}\" - enjoy your meal out!")

    # Add pregnancy tip (only if pregnancy tracking is enabled)
    if PREGNANCY_ENABLED:
        week = calculate_week(target_date)
        if week is not None:
            tip = get_weekly_tip(week)
            if conflicts or meal_events:
                lines.append("")
            lines.append(f"Tip: {tip}")

    return "\n".join(lines)