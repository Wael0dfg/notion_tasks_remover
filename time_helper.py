from datetime import datetime, timedelta
from logger import log_error

# Algeria is UTC+1
ALGERIA_OFFSET = timedelta(hours=1)

WEEKDAYS = [
    "monday", "tuesday", "wednesday",
    "thursday", "friday", "saturday", "sunday"
]

def get_now_algerian():
    """Returns the current datetime in Algeria (UTC+1)"""
    return datetime.utcnow() + ALGERIA_OFFSET

def get_target_datetime(hour, minute):
    """Returns the next scheduled datetime in Algeria for a given hour and minute"""
    now = get_now_algerian()
    target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if target <= now:
        target += timedelta(days=1)
    return target

def weekday_name_to_index(name):
    try:
        return WEEKDAYS.index(name.lower())
    except ValueError:
        log_error(f"Invalid weekday name: {name}")
        return -1

def is_time_to_run(run_time: str, now: datetime) -> bool:
    try:
        hour, minute = map(int, run_time.strip().split(":"))
        return now.hour == hour and now.minute == minute
    except Exception:
        log_error(f"Invalid run_time format: {run_time}")
        return False
