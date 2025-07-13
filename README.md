# Notion Tasks Remover

**Notion Tasks Remover** is a Python automation tool for Notion that automatically cleans your task pages based on your settings. It supports:

- ✅ Daily cleanup of to-do blocks
- 📅 Weekly (week-x) cleanup based on selected weekdays
- 🎯 Precise control using start and end block IDs
- 🔁 Runs continuously and logs errors & actions

---

## 📦 Features

### 🗓 Daily Cleanup
- Moves **unchecked** to-dos from the first column to the third column
- Deletes **checked** to-dos from the first column

### 📆 Weekly Cleanup (Week X)
- On specified weekdays, deletes **checked** to-dos from **second and third** columns

### 📌 Block Range Filtering
- You can define a `start_block_id` and `end_block_id` to limit which part of the page is processed
- If block IDs are missing or incorrect, the full page is used

---

## ⚙️ Configuration (settings.json)

Your configuration file should look like this:

```json
{
  "notion": {
    "page_id": "Your Page ID here",
    "token_v2": "Your Token_V2 here"
  },
  "daily": {
    "enabled": true,
    "run_time": "09:00"
  },
  "week": {
    "enabled": true,
    "week_days": ["sunday", "wednesday"],
    "run_time": "11:30"
  },
  "block_scope": {
    "start_block_id": "aabbccddeeff00112233445566778899",
    "end_block_id": "11223344556677889900aabbccddeeff"
  }
}
