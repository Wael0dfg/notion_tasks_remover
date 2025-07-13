from logger import log_error

def normalize_block_id(block_id):
    """Converts a compact Notion block ID to a hyphenated UUID format."""
    if not block_id:
        return None
    block_id = block_id.replace("-", "")
    if len(block_id) != 32:
        return block_id  # return as-is if invalid length
    return f"{block_id[0:8]}-{block_id[8:12]}-{block_id[12:16]}-{block_id[16:20]}-{block_id[20:]}"


def get_blocks_between_ids(blocks, start_id=None, end_id=None):
    if not blocks:
        return []

    ordered = list(blocks.items())
    start_index = 0
    end_index = len(ordered)

    normalized_start = normalize_block_id(start_id)
    normalized_end = normalize_block_id(end_id)

    if normalized_start:
        for i, (block_id, _) in enumerate(ordered):
            if block_id == normalized_start:
                start_index = i
                break
        else:
            log_error(f"Start block ID '{start_id}' not found. Using start of page.")
            start_index = 0

    if normalized_end:
        for i, (block_id, _) in enumerate(ordered):
            if block_id == normalized_end:
                end_index = i
                break
        else:
            log_error(f"End block ID '{end_id}' not found. Using end of page.")
            end_index = len(ordered)

    if start_index >= end_index:
        log_error(f"Invalid block range: start={start_index}, end={end_index}")
        return []

    return dict(ordered[start_index:end_index])


def get_checked_todos_in_column(blocks, column_id):
    todos = []
    for block_id, block_data in blocks.items():
        value = block_data.get("value", {})
        if value.get("type") == "to_do" and value.get("parent_id") == column_id:
            checked_prop = value.get("properties", {}).get("checked")
            is_checked = checked_prop and checked_prop[0][0] == "Yes"
            if is_checked:
                todos.append((block_id, block_data))
    return todos


def get_column_list_and_todos(blocks):
    ordered = list(blocks.items())
    first_divider_idx = None
    second_divider_idx = None
    column_list_id = None
    left_column_id = None
    third_column_id = None
    left_column_todos = []

    for idx, (block_id, block_data) in enumerate(ordered):
        block_type = block_data.get("value", {}).get("type")
        if block_type == "divider":
            if first_divider_idx is None:
                first_divider_idx = idx
            elif second_divider_idx is None:
                second_divider_idx = idx
                break

    if first_divider_idx is None:
        return None, None, None, []

    scan_range = ordered[first_divider_idx + 1:second_divider_idx] if second_divider_idx else ordered[first_divider_idx + 1:]

    for block_id, block_data in scan_range:
        value = block_data.get("value", {})
        if value.get("type") == "column_list":
            column_list_id = block_id
            break

    if not column_list_id:
        return None, None, None, []

    columns = [
        (block_id, block_data)
        for block_id, block_data in ordered
        if block_data.get("value", {}).get("type") == "column"
        and block_data.get("value", {}).get("parent_id") == column_list_id
    ]

    if len(columns) < 3:
        return column_list_id, None, None, []

    left_column_id = columns[0][0]
    third_column_id = columns[2][0]

    children_map = {}
    for block_id, block_data in blocks.items():
        parent_id = block_data.get("value", {}).get("parent_id")
        if parent_id:
            children_map.setdefault(parent_id, []).append(block_id)

    def collect_todos_recursively(parent_id):
        for child_id in children_map.get(parent_id, []):
            child_data = blocks[child_id]
            value = child_data.get("value", {})
            block_type = value.get("type")

            if block_type == "to_do":
                checked_prop = value.get("properties", {}).get("checked")
                is_checked = checked_prop and checked_prop[0][0] == "Yes"
                left_column_todos.append((child_id, child_data, is_checked))
            else:
                collect_todos_recursively(child_id)

    collect_todos_recursively(left_column_id)

    return column_list_id, left_column_id, third_column_id, left_column_todos
