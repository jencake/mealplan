from datetime import date, datetime, timedelta
from .schedule import Meal, parse_time, format_time


class Rule:
    def apply(self, meals: list[Meal], target_date: date) -> list[Meal]:
        return meals


class MaxTimeRule(Rule):
    """Clamp a named meal to no later than a given time string."""
    def __init__(self, meal_name: str, latest: str):
        self.meal_name = meal_name
        self.latest = parse_time(latest)

    def apply(self, meals, target_date):
        for meal in meals:
            if meal.name == self.meal_name:
                t = parse_time(meal.time)
                if t > self.latest:
                    meal.time = format_time(self.latest)
        return meals


class MinSpacingRule(Rule):
    """Ensure consecutive food meals are at least N hours apart."""
    def __init__(self, min_hours: float):
        self.min_spacing = timedelta(hours=min_hours)

    SKIP = {"Bedtime", "Workout", "Pre-Workout"}

    def apply(self, meals, target_date):
        food = [m for m in meals if m.name not in self.SKIP]
        food.sort(key=lambda m: parse_time(m.time))

        for i in range(1, len(food)):
            prev_dt = datetime.combine(target_date, parse_time(food[i-1].time))
            curr_dt = datetime.combine(target_date, parse_time(food[i].time))
            if curr_dt - prev_dt < self.min_spacing:
                food[i].time = format_time((prev_dt + self.min_spacing).time())

        return meals


class SkipLateSnackRule(Rule):
    """Remove snacks scheduled after a given hour."""
    def __init__(self, after_hour: int = 19):
        self.after_hour = after_hour

    def apply(self, meals, target_date):
        meals[:] = [
            m for m in meals
            if not (m.name in {"Morning Snack", "Afternoon Snack"}
                    and parse_time(m.time).hour >= self.after_hour)
        ]
        return meals


def apply_rules(meals: list[Meal], rules: list[Rule], target_date: date) -> list[Meal]:
    for rule in rules:
        meals = rule.apply(meals, target_date)
    return meals
