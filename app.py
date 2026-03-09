from datetime import date, timedelta
from functools import wraps
import os

from flask import Flask, Response, request
from mealplan.schedule import get_meals_for_day
from mealplan.formatter import format_schedule, CalendarEvent
from mealplan.cli import fetch_calendar_events
from mealplan.rule_engine import apply_rules, DEFAULT_RULES
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)


def check_auth(password):
    return password == os.environ.get("APP_PASSWORD")

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.password):
            return Response("Unauthorized", 401, {"WWW-Authenticate": 'Basic realm="mealplan"'})
        return f(*args, **kwargs)
    return decorated


@app.route("/")
@app.route("/<day>")
@require_auth
def show(day=None):
    if day:
        weekdays = ["monday","tuesday","wednesday","thursday","friday","saturday","sunday"]
        if day.lower() not in weekdays:
            return "Invalid day", 400
        today = date.today()
        target_weekday = weekdays.index(day.lower())
        delta = target_weekday - today.weekday()
        target_date = today + timedelta(days=delta)
    else:
        target_date = date.today()

    day_name = target_date.strftime("%A")
    meals = get_meals_for_day(day_name)
    meals = apply_rules(meals, DEFAULT_RULES, target_date)
    events = fetch_calendar_events(target_date)
    output = format_schedule(target_date, meals, events)
    return f"<pre style='font-family:monospace;padding:1rem'>{output}</pre>"