"""Pregnancy week calculation and developmental milestones."""

from datetime import date
from dataclasses import dataclass
from typing import Optional

from .config import PREGNANCY_ENABLED, get_pregnancy_due_date


@dataclass
class TrimesterInfo:
    """Information about a trimester."""
    number: int
    name: str
    extra_calories: int
    protein_range: str
    focus: str
    tips: list[str]


TRIMESTERS = {
    1: TrimesterInfo(
        number=1,
        name="1st Trimester",
        extra_calories=0,
        protein_range="60-75g",
        focus="Folate, managing nausea, small frequent meals",
        tips=[
            "Ginger for nausea",
            "Bland foods if queasy",
            "Prenatal vitamin timing matters",
        ],
    ),
    2: TrimesterInfo(
        number=2,
        name="2nd Trimester",
        extra_calories=340,
        protein_range="75-100g",
        focus="Iron absorption, energy maintenance, baby's rapid growth",
        tips=[
            "Pair iron with vitamin C",
            "Stay hydrated",
            "Calcium for bones",
        ],
    ),
    3: TrimesterInfo(
        number=3,
        name="3rd Trimester",
        extra_calories=450,
        protein_range="100g+",
        focus="Smaller meals (less stomach room), calcium, preparing for labor",
        tips=[
            "Eat smaller portions more frequently",
            "Dates for labor prep",
            "Omega-3s for brain development",
        ],
    ),
}


@dataclass
class Milestone:
    """Baby development milestone."""
    week_start: int
    week_end: int
    baby_size: str
    development: str


MILESTONES = [
    Milestone(13, 14, "Lemon", "Fingerprints forming, can suck thumb"),
    Milestone(15, 16, "Apple", "Hearing developing, can sense light"),
    Milestone(17, 18, "Pear", "Fat layer forming, can yawn"),
    Milestone(19, 20, "Banana", "Vernix coating, halfway point!"),
    Milestone(21, 22, "Papaya", "Eyebrows visible, sleep cycles"),
    Milestone(23, 24, "Grapefruit", "Lungs developing, responds to sounds"),
    Milestone(25, 26, "Cauliflower", "Eyes open, brain rapid growth"),
    Milestone(27, 28, "Eggplant", "Can dream, practices breathing"),
    Milestone(29, 30, "Butternut squash", "Bones hardening, head-down position"),
    Milestone(31, 32, "Coconut", "Fingernails complete, gaining ~0.5 lb/week"),
    Milestone(33, 34, "Pineapple", "Immune system developing, less room to move"),
    Milestone(35, 36, "Honeydew", "Lungs nearly mature, dropping into pelvis"),
    Milestone(37, 38, "Winter melon", "Full term! Ready for birth"),
    Milestone(39, 40, "Watermelon", "Fully developed, any day now!"),
]


def calculate_week(target_date: date) -> Optional[int]:
    """Calculate pregnancy week from due date.

    Week = 40 - floor(days_until_due_date / 7)
    Returns None if pregnancy tracking is disabled or no due date set.
    """
    due_date = get_pregnancy_due_date()
    if due_date is None:
        return None
    days_until_due = (due_date - target_date).days
    if days_until_due < 0:
        return 40  # Past due date
    week = 40 - (days_until_due // 7)
    return max(1, min(40, week))


def get_trimester(week: int) -> TrimesterInfo:
    """Get trimester info for a given week."""
    if week <= 13:
        return TRIMESTERS[1]
    elif week <= 27:
        return TRIMESTERS[2]
    else:
        return TRIMESTERS[3]


def get_milestone(week: int) -> Optional[Milestone]:
    """Get the development milestone for a given week."""
    for milestone in MILESTONES:
        if milestone.week_start <= week <= milestone.week_end:
            return milestone
    return None


def get_weekly_tip(week: int) -> str:
    """Get a contextual tip based on current pregnancy week."""
    milestone = get_milestone(week)
    trimester = get_trimester(week)

    if milestone:
        return f"Week {week}: Baby is the size of a {milestone.baby_size.lower()}! {milestone.development}"

    # Fallback to trimester tip
    if trimester.tips:
        import random
        return random.choice(trimester.tips)

    return f"Week {week} of pregnancy - {trimester.focus}"
