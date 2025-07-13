import requests

def fetch_page_blocks(page_id, token_v2):
    url = f"https://www.notion.so/api/v3/loadPageChunk"

    payload = {
        "pageId": page_id,
        "limit": 100,
        "chunkNumber": 0,
        "verticalColumns": False
    }

    headers = {
        "Content-Type": "application/json",
        "cookie": f"token_v2={token_v2}"
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code != 200:
        raise Exception(f"Failed to fetch page blocks: {response.status_code} {response.text}")

    data = response.json()
    return data["recordMap"]["block"]
