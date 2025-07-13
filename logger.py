import os
from datetime import datetime

LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")
DAILY_LOG = os.path.join(LOG_DIR, "actions_daily.log")
WEEK_LOG = os.path.join(LOG_DIR, "actions_week.log")
ERROR_LOG = os.path.join(LOG_DIR, "errors.log")

os.makedirs(LOG_DIR, exist_ok=True)

def log_action(mode, action_type, name, block_id):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    file = DAILY_LOG if mode == "daily" else WEEK_LOG
    with open(file, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {action_type.upper()}: \"{name}\" (ID: {block_id})\n")

def log_error(message, block_id=None):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(ERROR_LOG, "a", encoding="utf-8") as f:
        if block_id:
            f.write(f"[{timestamp}] ERROR for {block_id}: {message}\n")
        else:
            f.write(f"[{timestamp}] ERROR: {message}\n")