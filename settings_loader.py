import json
import os

VALID_WEEKDAYS = [
    "monday", "tuesday", "wednesday",
    "thursday", "friday", "saturday", "sunday"
]

LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

def load_settings(filename="settings.json"):
    # Always resolve the full path relative to this file
    base_dir = os.path.dirname(os.path.abspath(__file__))
    settings_path = os.path.join(base_dir, filename)

    if not os.path.exists(settings_path):
        raise FileNotFoundError(f"Settings file not found: {settings_path}")

    with open(settings_path, "r", encoding="utf-8") as file:
        settings = json.load(file)

    # Validate and normalize Notion credentials
    notion = settings.get("notion", {})
    if not notion.get("page_id") or not notion.get("token_v2"):
        raise ValueError("Notion page_id and token_v2 must be provided.")

    notion["page_id"] = normalize_page_id(notion["page_id"])
    settings["notion"] = notion

    # Validate weekday names
    week_config = settings.get("week", {})
    validated_week_days = []
    for day in week_config.get("week_days", []):
        if day.lower() in VALID_WEEKDAYS:
            validated_week_days.append(day.lower())
        else:
            log_error(f"Invalid weekday in settings: {day}")
    settings["week"]["week_days"] = validated_week_days

    # Ensure block_scope keys exist
    block_scope = settings.get("block_scope", {})
    settings["block_scope"] = {
        "start_block_id": block_scope.get("start_block_id"),
        "end_block_id": block_scope.get("end_block_id")
    }

    return settings

def normalize_page_id(raw_id):
    # If already dashed and valid
    if "-" in raw_id and len(raw_id) == 36:
        return raw_id
    if len(raw_id) != 32:
        log_error(f"Invalid Notion page ID length: {raw_id}")
        return raw_id  # Leave unchanged if it's not valid

    # Convert to dashed format: 8-4-4-4-12
    return f"{raw_id[0:8]}-{raw_id[8:12]}-{raw_id[12:16]}-{raw_id[16:20]}-{raw_id[20:]}"

def log_error(message):
    error_path = os.path.join(LOG_DIR, "errors.log")
    with open(error_path, "a", encoding="utf-8") as error_log:
        error_log.write(f"[ERROR] {message}\n")
