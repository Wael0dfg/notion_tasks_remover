import requests
import time
from logger import log_action, log_error

def delete_block(block_id, name="(unknown)", mode="daily", token=None):
    if token is None:
        log_error("No token provided to delete_block()", block_id)
        return False

    headers = {
        "cookie": f"token_v2={token}",
        "Content-Type": "application/json"
    }

    url = "https://www.notion.so/api/v3/deleteBlocks"
    data = {
        "blockIds": [block_id],
        "permanentlyDelete": True
    }

    try:
        res = requests.post(url, json=data, headers=headers)
        res.raise_for_status()
        log_action(mode, "DELETED", name, block_id)
        return True
    except Exception as e:
        log_error(f"Failed to delete: {e}", block_id)
        return False


def move_block(block_id, new_parent_id, old_parent_id=None, name="(unknown)", token=None):
    if token is None:
        log_error("No token provided to move_block()", block_id)
        return False

    headers = {
        "cookie": f"token_v2={token}",
        "Content-Type": "application/json"
    }

    url = "https://www.notion.so/api/v3/submitTransaction"

    ops = []

    if old_parent_id:
        ops.append({
            "id": old_parent_id,
            "table": "block",
            "path": ["content"],
            "command": "listRemove",
            "args": {
                "id": block_id
            }
        })

    ops.append({
        "id": new_parent_id,
        "table": "block",
        "path": ["content"],
        "command": "listAfter",
        "args": {
            "id": block_id,
            "after": None
        }
    })

    ops.append({
        "id": block_id,
        "table": "block",
        "path": [],
        "command": "update",
        "args": {
            "parent_id": new_parent_id,
            "parent_table": "block"
        }
    })

    try:
        res = requests.post(url, json={"operations": ops}, headers=headers)
        res.raise_for_status()
        log_action("daily", "MOVED", name, block_id)
        return True
    except Exception as e:
        log_error(f"Failed to move: {e}", block_id)
        return False


def process_daily_todos(left_column_id, third_column_id, todos, token):
    deleted = 0
    moved = 0

    for block_id, block_data, is_checked in todos:
        props = block_data.get("value", {}).get("properties", {})
        name = props.get("title", [["(Untitled)"]])[0][0]

        if is_checked:
            if delete_block(block_id, name, mode="daily", token=token):
                deleted += 1
        else:
            if move_block(block_id, third_column_id, old_parent_id=left_column_id, name=name, token=token):
                moved += 1

        time.sleep(0.3)

    print(f"[SUMMARY] Daily: Deleted {deleted} checked to-dos, moved {moved} unchecked.")


def process_weekly_cleanup(checked_todos, column_labels, token):
    deleted = 0

    for block_id, block_data in checked_todos:
        props = block_data.get("value", {}).get("properties", {})
        name = props.get("title", [["(Untitled)"]])[0][0]

        parent_id = block_data.get("value", {}).get("parent_id")
        column_name = column_labels.get(parent_id, "Unknown Column")
        display_name = f"{name} ({column_name})"

        if delete_block(block_id, display_name, mode="week", token=token):
            deleted += 1
        time.sleep(0.3)

    print(f"[SUMMARY] Week: Deleted {deleted} checked to-dos from second and third columns.")
