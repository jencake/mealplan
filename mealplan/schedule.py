"""Meal schedule data and day lookup."""

import copy
import re
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from pathlib import Path
from typing import Optional

from . import config


@dataclass
class Meal:
    """A single meal entry."""
    time: str
    name: str
    description: str
    notes: Optional[str] = None


# Workout meal blocks per workout day — only injected when workout is enabled
WORKOUT_BLOCKS: dict[str, list] = {
    "wednesday": [
        Meal("3:30pm", "Pre-Workout", "Pre-workout powder + water"),
        Meal("4:30pm", "Workout", "30-minute workout"),
        Meal("5:00pm", "Post-Workout Smoothie", "1 cup milk + 2 scoops vanilla protein + 1 cup mango + splash OJ + 1 scoop collagen", "Tropical Mango"),
    ],
    "friday": [
        Meal("3:30pm", "Pre-Workout", "Pre-workout powder + water"),
        Meal("4:30pm", "Workout", "30-minute workout"),
        Meal("5:00pm", "Post-Workout Smoothie", "1 cup milk + 2 scoops vanilla protein + 1 cup strawberry banana + 1 scoop collagen", "Strawberry Banana"),
    ],
    "sunday": [
        Meal("3:30pm", "Pre-Workout", "Pre-workout powder + water"),
        Meal("4:30pm", "Workout", "30-minute workout"),
        Meal("5:00pm", "Post-Workout Smoothie", "1 cup milk + 2 scoops vanilla protein + 1 cup blueberry + 1 tsp honey + 1 scoop collagen", "Blueberry Vanilla"),
    ],
}

# Fallback workout block for days not in WORKOUT_BLOCKS
DEFAULT_WORKOUT_BLOCK = [
    Meal("3:30pm", "Pre-Workout", "Pre-workout powder + water"),
    Meal("4:30pm", "Workout", "30-minute workout"),
    Meal("5:00pm", "Post-Workout Smoothie", "1 cup milk + 2 scoops vanilla protein + 1 scoop collagen"),
]


def validate_workout_config() -> None:
    """Warn if any configured workout days don't have a custom workout block.

    Called at startup so misconfigured days are surfaced immediately rather
    than silently falling back without the user noticing.
    """
    if not config.WORKOUT_ENABLED:
        return
    uncovered = config.WORKOUT_DAYS - WORKOUT_BLOCKS.keys()
    if uncovered:
        days = ", ".join(sorted(uncovered))
        import sys
        print(
            f"Warning: No custom workout block for {days}. "
            f"Using default block (pre-workout + workout + generic smoothie). "
            f"Add entries to WORKOUT_BLOCKS in schedule.py to customize.",
            file=sys.stderr,
        )

# Matcha latte block — injected on non-workout days (carries collagen on those days)
MATCHA_BLOCK = Meal("3:00pm", "Matcha Latte", "1 cup oat milk + 1 tsp matcha + 1 scoop collagen")


# Monday-Thursday base schedules (no workout or matcha meals — injected dynamically)
SIMPLE_PREP = {
    "monday": [
        Meal("7:30am", "Breakfast", "1 cup Greek yogurt + ½ cup berries + ¼ cup granola"),
        Meal("10:00am", "Morning Snack", "1 apple + 2 tbsp Nutella"),
        Meal("12:30pm", "Lunch", "1 can Progresso chicken wild rice soup + 1 hard-boiled egg + 1 slice whole grain toast"),
        Meal("3:00pm", "Afternoon Snack", "½ cup cottage cheese + ½ cup pineapple"),
        Meal("6:30pm", "Dinner", "1 cup tofu with 1 tsp sesame oil & 1 tbsp soy sauce + 1 cup brown rice + 1 cup steamed cabbage"),
        Meal("8:30pm", "Evening Snack", "1 banana + 10 almonds"),
        Meal("10:30pm", "Bedtime", ""),
    ],
    "tuesday": [
        Meal("7:30am", "Breakfast", "1 cup Greek yogurt + ½ cup berries + ¼ cup granola"),
        Meal("10:00am", "Morning Snack", "¼ cup candied almonds"),
        Meal("12:30pm", "Lunch", "1 can Progresso chicken wild rice soup + 1 hard-boiled egg + 1 slice whole grain toast"),
        Meal("3:00pm", "Afternoon Snack", "6 oz yogurt + 1 tbsp honey"),
        Meal("6:30pm", "Dinner", "1 cup tofu with 1 tsp sesame oil & 1 tbsp soy sauce + 1 cup brown rice + 1 cup steamed carrots"),
        Meal("8:30pm", "Evening Snack", "1 cup warm milk + 1 tsp honey"),
        Meal("10:30pm", "Bedtime", ""),
    ],
    "wednesday": [
        Meal("7:30am", "Breakfast", "1 cup Greek yogurt + ½ cup berries + ¼ cup granola"),
        Meal("10:00am", "Morning Snack", "1 string cheese + ½ cup grapes"),
        Meal("12:30pm", "Lunch", "1 can Progresso chicken wild rice soup + 1 hard-boiled egg + 1 slice whole grain toast"),
        Meal("3:00pm", "Afternoon Snack", "½ cup cottage cheese + ½ cup pineapple"),
        Meal("6:30pm", "Dinner", "1 cup tofu with 1 tsp sesame oil & 1 tbsp soy sauce + 1 cup brown rice + 1 cup steamed cabbage"),
        Meal("8:30pm", "Evening Snack", "1 banana + 10 almonds"),
        Meal("10:30pm", "Bedtime", ""),
    ],
    "thursday": [
        Meal("7:30am", "Breakfast", "1 cup Greek yogurt + ½ cup berries + ¼ cup granola"),
        Meal("10:00am", "Morning Snack", "¼ cup candied walnuts"),
        Meal("12:30pm", "Lunch", "1 can Progresso chicken wild rice soup + 1 hard-boiled egg + 1 slice whole grain toast"),
        Meal("3:00pm", "Afternoon Snack", "6 oz yogurt + 1 tbsp honey"),
        Meal("6:30pm", "Dinner", "1 cup tofu with 1 tsp sesame oil & 1 tbsp soy sauce + 1 cup brown rice + 1 cup steamed carrots"),
        Meal("8:30pm", "Evening Snack", "1 cup warm milk + 1 tsp honey"),
        Meal("10:30pm", "Bedtime", ""),
    ],
}

# Friday-Sunday base schedules (no workout or matcha meals — injected dynamically)
INDULGENT = {
    "friday": [
        Meal("7:30am", "Breakfast", "2 scrambled eggs + 1 slice whole wheat toast + ½ avocado + ½ orange"),
        Meal("10:00am", "Morning Snack", "¼ cup candied cashews"),
        Meal("12:30pm", "Lunch", "Turkey sandwich: 3 oz turkey + ½ avocado ✓ + 2 slices whole wheat"),
        Meal("3:00pm", "Afternoon Snack", "Smoothie: 1 cup spinach + 1 banana + 1 cup milk"),
        Meal("6:30pm", "Dinner", "4 oz roast chicken + 1 cup roasted potatoes + ½ orange ✓"),
        Meal("8:30pm", "Evening Snack", "1 banana + 10 almonds"),
        Meal("10:30pm", "Bedtime", ""),
    ],
    "saturday": [
        Meal("7:30am", "Breakfast", "2 scrambled eggs + 1 slice whole wheat toast + ½ avocado + ½ orange"),
        Meal("10:00am", "Morning Snack", "1 cheese stick + 6 crackers + ½ orange ✓"),
        Meal("12:30pm", "Lunch", "Caesar salad: 2 cups romaine + 3 oz chicken + ½ avocado ✓ + 2 tbsp dressing"),
        Meal("3:00pm", "Afternoon Snack", "¼ cup hummus + 1 cup veggie sticks"),
        Meal("6:30pm", "Dinner", "4 oz roast chicken + 1 cup roasted potatoes"),
        Meal("8:30pm", "Evening Snack", "1 oz cheese + 6 crackers"),
        Meal("10:30pm", "Bedtime", ""),
    ],
    "sunday": [
        Meal("7:30am", "Breakfast", "2 scrambled eggs + 1 slice whole wheat toast + ½ avocado + ½ orange"),
        Meal("10:00am", "Morning Snack", "1 apple + 2 tbsp Nutella"),
        Meal("12:30pm", "Lunch", "Turkey sandwich: 3 oz turkey + ½ avocado ✓ + 2 slices whole wheat"),
        Meal("3:00pm", "Afternoon Snack", "Smoothie: 1 cup spinach + 1 banana + 1 cup milk"),
        Meal("6:30pm", "Dinner", "4 oz roast chicken + 1 cup roasted potatoes"),
        Meal("8:30pm", "Evening Snack", "1 cup warm milk + 1 tsp honey + ½ orange ✓"),
        Meal("10:30pm", "Bedtime", ""),
    ],
}


def _strip_collagen(meal: Meal) -> Meal:
    """Return a copy of the meal with collagen removed from the description."""
    desc = re.sub(r'\s*\+\s*1 scoop collagen', '', meal.description, flags=re.IGNORECASE).strip()
    return Meal(time=meal.time, name=meal.name, description=desc, notes=meal.notes)


def get_meals_for_day(day_name: str) -> list[Meal]:
    """Get the meal schedule for a given day, injecting workout/matcha blocks from config."""
    day_lower = day_name.lower()

    if day_lower in SIMPLE_PREP:
        base = copy.deepcopy(SIMPLE_PREP[day_lower])
    elif day_lower in INDULGENT:
        base = copy.deepcopy(INDULGENT[day_lower])
    else:
        raise ValueError(f"Unknown day: {day_name}")

    is_workout = config.WORKOUT_ENABLED and day_lower in config.WORKOUT_DAYS

    if is_workout and day_lower in WORKOUT_BLOCKS:
        base.extend(copy.deepcopy(WORKOUT_BLOCKS[day_lower]))
    elif is_workout:
        base.extend(copy.deepcopy(DEFAULT_WORKOUT_BLOCK))
    else:
        # Non-workout day: inject matcha latte (with or without collagen)
        base.append(copy.deepcopy(MATCHA_BLOCK))

    # Strip collagen from all meals if disabled
    if not config.COLLAGEN_ENABLED:
        base = [_strip_collagen(m) for m in base]

    base.sort(key=lambda m: parse_time(m.time))
    return base


def is_workout_day(day_name: str) -> bool:
    """Check if this is a workout day per config."""
    return config.WORKOUT_ENABLED and day_name.lower() in config.WORKOUT_DAYS


def parse_time(time_str: str) -> time:
    """Parse time string like '7:30am' into a time object."""
    time_str = time_str.lower().strip()
    if time_str.endswith("am"):
        time_str = time_str[:-2]
        is_pm = False
    elif time_str.endswith("pm"):
        time_str = time_str[:-2]
        is_pm = True
    else:
        is_pm = False

    if ":" in time_str:
        hour, minute = time_str.split(":")
        hour = int(hour)
        minute = int(minute)
    else:
        hour = int(time_str)
        minute = 0

    if is_pm and hour != 12:
        hour += 12
    elif not is_pm and hour == 12:
        hour = 0

    return time(hour, minute)


def format_time(t: time) -> str:
    """Format a time object as '5:30pm' style string."""
    hour = t.hour
    minute = t.minute
    if hour == 0:
        return f"12:{minute:02d}am"
    elif hour < 12:
        return f"{hour}:{minute:02d}am"
    elif hour == 12:
        return f"12:{minute:02d}pm"
    else:
        return f"{hour - 12}:{minute:02d}pm"


def is_iron_day(target_date: date, overrides_dir: Path) -> bool:
    """Check if iron should be taken today (every other day logic).

    Uses a deterministic pattern: even days (since last iron intake) are iron days.
    If iron was manually logged on a non-iron day, that resets the schedule.
    Override files can skip iron if they contain "skip iron" or similar.
    """
    # Check for explicit skip in today's override
    override_file = overrides_dir / f"{target_date.isoformat()}.md"
    if override_file.exists():
        try:
            content = override_file.read_text().lower()
            if "skip iron" in content or "no iron" in content:
                return False
        except Exception:
            pass

    # Find the most recent day iron was actually taken (via override log)
    # Scan backwards through all available override files
    last_iron_date = None
    for days_back in range(1, 365):  # Scan up to a year back
        check_date = target_date - timedelta(days=days_back)
        check_file = overrides_dir / f"{check_date.isoformat()}.md"
        if check_file.exists():
            try:
                content = check_file.read_text().lower()
                if "iron supplement" in content:
                    last_iron_date = check_date
                    break
            except Exception:
                pass

    # If we found a recent iron intake, use that as reference
    if last_iron_date:
        days_since_iron = (target_date - last_iron_date).days
        # Every other day pattern: skip day 1, take day 2, skip day 3, take day 4, etc.
        # Even days since last iron (excluding day 0) = iron day
        return days_since_iron > 0 and days_since_iron % 2 == 0

    # Fallback: use original start date for deterministic pattern
    # Start date: 2026-03-02 (when feature was implemented)
    start_date = date(2026, 3, 2)
    days_since_start = (target_date - start_date).days

    # Even days = iron day, odd days = no iron
    return days_since_start % 2 == 0


def find_iron_slot(
    meals: list["Meal"],
    calendar_events: list,
    target_date: date,
) -> Optional[str]:
    """Find optimal iron time: 2h after meal, 1h before next, no calendar conflict.

    Rules:
    - At least 2 hours after the previous meal
    - At least 1 hour before the next meal
    - Minimum 3-hour gap between meals required
    - Avoid calendar conflicts

    Returns time string like "5:30pm" or None if no valid slot found.
    """
    # Filter out non-food meals (Bedtime, Workout, etc.)
    food_meals = [
        m for m in meals
        if m.name not in {"Bedtime", "Workout", "Pre-Workout"}
    ]

    if len(food_meals) < 2:
        return None

    # Sort meals by time
    sorted_meals = sorted(food_meals, key=lambda m: parse_time(m.time))

    # Find gaps >= 3 hours between consecutive meals
    for i in range(len(sorted_meals) - 1):
        meal1 = sorted_meals[i]
        meal2 = sorted_meals[i + 1]

        t1 = parse_time(meal1.time)
        t2 = parse_time(meal2.time)

        # Convert to datetime for arithmetic
        dt1 = datetime.combine(target_date, t1)
        dt2 = datetime.combine(target_date, t2)

        gap = dt2 - dt1
        gap_hours = gap.total_seconds() / 3600

        if gap_hours < 3:
            continue  # Gap too small

        # Iron time: 2 hours after meal1
        iron_dt = dt1 + timedelta(hours=2)
        iron_time = iron_dt.time()

        # Verify at least 1 hour before meal2
        if (dt2 - iron_dt).total_seconds() < 3600:
            continue

        # Check calendar conflicts
        has_conflict = False
        for event in calendar_events:
            if hasattr(event, 'is_all_day') and event.is_all_day:
                continue
            event_start = event.start.time() if hasattr(event.start, 'time') else event.start
            event_end = event.end.time() if hasattr(event.end, 'time') else event.end
            if event_start <= iron_time <= event_end:
                has_conflict = True
                break

        if not has_conflict:
            return format_time(iron_time)

    return None  # No valid slot found