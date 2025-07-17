import json
import os
import re
import base64
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.singaporepools.com.sg/en/product/sr/Pages/toto_results.aspx"
RESULTS_JSON_PATH = "docs/toto_result.json"
DRAW_URLS_PATH = "draw_urls.txt"

def load_existing_draw_numbers():
    if not os.path.exists(RESULTS_JSON_PATH):
        return set()
    with open(RESULTS_JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return {str(entry["draw_number"]) for entry in data}

def fetch_draw_options():
    response = requests.get(BASE_URL, timeout=10)
    soup = BeautifulSoup(response.text, "html.parser")
    options = soup.select("select[id$='_ddlPastDraws'] > option")
    print(f"[DEBUG] Total <option> tags found: {len(options)}")
    return options

def decode_draw_number(sppl_value):
    try:
        decoded = base64.b64decode(sppl_value).decode("utf-8")
        match = re.search(r"DrawNumber=(\d+)", decoded)
        return match.group(1) if match else None
    except Exception:
        return None

def main():
    existing_draws = load_existing_draw_numbers()
    print(f"[✓] Found {len(existing_draws)} results in {RESULTS_JSON_PATH}")

    options = fetch_draw_options()

    new_urls = []
    for opt in options:
        value = opt.get("value")
        if not value:
            continue
        draw_number = decode_draw_number(value)
        if draw_number is None:
            continue
        full_url = f"{BASE_URL}?sppl={value}"
        if draw_number not in existing_draws:
            new_urls.append(full_url)

    if new_urls:
        with open(DRAW_URLS_PATH, "w", encoding="utf-8") as f:
            for url in new_urls:
                f.write(url + "\n")
        print(f"[✓] {len(new_urls)} new draw URLs written to {DRAW_URLS_PATH}")
        print("[DEBUG] First 3 new draws:")
        for u in new_urls[:3]:
            print(f"  → {u}")
    else:
        print("[✓] No new draws found. draw_urls.txt not updated.")

if __name__ == "__main__":
    print("[+] Fetching draw list...")
    main()
