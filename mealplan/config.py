"""Configuration settings from environment variables."""

import os
from datetime import date
from typing import Optional


# Core settings
WAKE_TIME = os.environ.get("MEALPLAN_WAKE_TIME", "7:00am")

# Pregnancy tracking (optional - disabled by default)
PREGNANCY_ENABLED = os.environ.get("MEALPLAN_PREGNANCY_ENABLED", "").lower() in (
    "1",
    "true",
    "yes",
)
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
