"""Configuration settings from environment variables."""

import os
from datetime import date
from typing import Optional


def _bool_env(key: str, default: bool) -> bool:
    val = os.environ.get(key)
    if val is None:
        return default
    return val.lower() in ("1", "true", "yes")


# Core settings
WAKE_TIME = os.environ.get("MEALPLAN_WAKE_TIME", "7:00am")

# Iron supplement scheduling (disabled by default)
IRON_ENABLED = _bool_env("MEALPLAN_IRON_ENABLED", False)

# Collagen supplement (disabled by default)
COLLAGEN_ENABLED = _bool_env("MEALPLAN_COLLAGEN_ENABLED", False)

# Workout scheduling (disabled by default)
WORKOUT_ENABLED = _bool_env("MEALPLAN_WORKOUT_ENABLED", False)

# Configurable workout days (default: mon,wed,fri)
_workout_days_str = os.environ.get("MEALPLAN_WORKOUT_DAYS", "mon,wed,fri")
_DAY_ALIASES = {
    "mon": "monday", "tue": "tuesday", "wed": "wednesday",
    "thu": "thursday", "fri": "friday", "sat": "saturday", "sun": "sunday",
}
WORKOUT_DAYS: set = {
    _DAY_ALIASES.get(d.strip().lower(), d.strip().lower())
    for d in _workout_days_str.split(",")
    if d.strip()
}

# Pregnancy tracking (optional - disabled by default)
PREGNANCY_ENABLED = _bool_env("MEALPLAN_PREGNANCY_ENABLED", False)
_due_date_str = os.environ.get("MEALPLAN_PREGNANCY_DUE_DATE")


def get_pregnancy_due_date() -> Optional[date]:
    """Get pregnancy due date from environment variable.

    Returns None if pregnancy tracking is disabled or due date not set.
    """
    if not PREGNANCY_ENABLED:
        return None
    if not _due_date_str:
        return None
    try:
        return date.fromisoformat(_due_date_str)
    except ValueError:
        return None