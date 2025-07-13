import time
from datetime import timedelta
from settings_loader import load_settings
from time_helper import get_now_algerian, get_target_datetime, is_time_to_run, weekday_name_to_index
from page_fetcher import fetch_page_blocks
from block_filter import get_blocks_between_ids, get_column_list_and_todos, get_checked_todos_in_column
from todo_remover import process_daily_todos, process_weekly_cleanup
from logger import log_error

def should_run_week_routine(config, now):
    today_index = now.weekday()
    week_days = config.get("week", {}).get("week_days", [])
    return any(weekday_name_to_index(day) == today_index for day in week_days)

def run_daily_routine(config):
    print("\n[✅] Running Daily Routine")
    page_id = config["notion"]["page_id"]
    token = config["notion"]["token_v2"]

    blocks = fetch_page_blocks(page_id, token)
    start_id = config["block_scope"].get("start_block_id")
    end_id = config["block_scope"].get("end_block_id")

    filtered_blocks = get_blocks_between_ids(blocks, start_id, end_id)
    if not filtered_blocks:
        log_error("Daily: Invalid or missing block range. Falling back to full page.")
        filtered_blocks = blocks

    # Extract columns and todos
    _, left_column_id, third_column_id, todos = get_column_list_and_todos(filtered_blocks)
    if not todos:
        print("[INFO] No to-dos found in left column.")
        return

    process_daily_todos(left_column_id, third_column_id, todos, config["notion"]["token_v2"])

def run_week_routine(config):
    print("\n[✅] Running Week X Routine")
    page_id = config["notion"]["page_id"]
    token = config["notion"]["token_v2"]

    blocks = fetch_page_blocks(page_id, token)
    start_id = config["block_scope"].get("start_block_id")
    end_id = config["block_scope"].get("end_block_id")

    filtered_blocks = get_blocks_between_ids(blocks, start_id, end_id)
    if not filtered_blocks:
        log_error("Week: Invalid or missing block range. Falling back to full page.")
        filtered_blocks = blocks

    column_list_id, left_column_id, third_column_id, _ = get_column_list_and_todos(filtered_blocks)

    if not column_list_id or not third_column_id:
        print("[INFO] Required columns not found.")
        return

    # Find second column
    second_column_id = None
    for block_id, block_data in filtered_blocks.items():
        val = block_data.get("value", {})
        if val.get("type") == "column" and val.get("parent_id") == column_list_id:
            if block_id != left_column_id and block_id != third_column_id:
                second_column_id = block_id
                break

    if not second_column_id:
        print("[INFO] Second column not found.")
        return

    checked_third = get_checked_todos_in_column(filtered_blocks, third_column_id)
    checked_second = get_checked_todos_in_column(filtered_blocks, second_column_id)
    combined = checked_third + checked_second

    if not combined:
        print("[INFO] No checked to-dos found in second or third columns.")
        return

    column_labels = {
        second_column_id: "Second Column",
        third_column_id: "Third Column"
    }

    process_weekly_cleanup(combined, column_labels, config["notion"]["token_v2"])

def format_timer(seconds):
    if seconds < 0:
        seconds = 0
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h:02d}h {m:02d}m {s:02d}s"

if __name__ == "__main__":
    config = load_settings()
    print("[🚀] pro_tasks_remover is running (Algerian Time)...")

    last_daily_run_date = None
    last_week_run_date = None

    while True:
        now = get_now_algerian()
        current_date = now.date()

        # Parse run times
        daily_hour, daily_min = map(int, config["daily"]["run_time"].split(":"))
        week_hour, week_min = map(int, config["week"]["run_time"].split(":"))

        # Compute target times
        daily_target = get_target_datetime(daily_hour, daily_min)
        week_target = get_target_datetime(week_hour, week_min)

        # Check if it's a valid weekday for weekly routine
        is_week_day = should_run_week_routine(config, now)

        # Calculate time left
        daily_remaining = int((daily_target - now).total_seconds())
        week_remaining = int((week_target - now).total_seconds()) if is_week_day else None

        # Countdown line
        line = f"\r[⏳] Daily in {format_timer(daily_remaining)}"
        if is_week_day:
            line += f" | Week-x in {format_timer(week_remaining)}"
        print(line.ljust(80), end="", flush=True)

        # Trigger daily once per day
        if config.get("daily", {}).get("enabled", False):
            if is_time_to_run(config["daily"]["run_time"], now):
                if last_daily_run_date != current_date:
                    run_daily_routine(config)
                    last_daily_run_date = current_date

        # Trigger week once per day (if it's a valid weekday)
        if config.get("week", {}).get("enabled", False):
            if is_week_day and is_time_to_run(config["week"]["run_time"], now):
                if last_week_run_date != current_date:
                    run_week_routine(config)
                    last_week_run_date = current_date

        time.sleep(1)
