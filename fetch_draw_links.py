import os
import json
import base64
import requests
from bs4 import BeautifulSoup

# Constants
URL = "https://www.singaporepools.com.sg/en/product/sr/Pages/toto_results.aspx"
DRAW_LIST_SELECTOR = "select[title='Select Draw Number'] option"
RESULTS_JSON_PATH = os.path.join("docs", "toto_result.json")
URLS_OUTPUT_PATH = "draw_urls.txt"
DRAW_URL_PREFIX = "https://www.singaporepools.com.sg/en/product/sr/Pages/toto_results.aspx?"

# Load existing results
if os.path.exists(RESULTS_JSON_PATH):
    with open(RESULTS_JSON_PATH, "r", encoding="utf-8") as f:
        existing_results = json.load(f)
else:
    existing_results = []

existing_draws = set(entry["draw_number"] for entry in existing_results)
print(f"[✓] Found {len(existing_draws)} results in {RESULTS_JSON_PATH}")

# Fetch page content
print("[+] Fetching draw list...")
response = requests.get(URL)
soup = BeautifulSoup(response.content, "html.parser")
options = soup.select(DRAW_LIST_SELECTOR)

print(f"[DEBUG] Total <option> tags found: {len(options)}")

valid_draws = []
for opt in options:
    val = opt.get("value", "")
    text = opt.get_text(strip=True)
    if not val.startswith("sppl="):
        continue
    encoded = val.replace("sppl=", "").strip()
    try:
        decoded = base64.b64decode(encoded).decode("utf-8")
        if "DrawNumber=" in decoded:
            draw_num = decoded.split("DrawNumber=")[-1]
            if draw_num not in existing_draws:
                full_url = f"{DRAW_URL_PREFIX}sppl={encoded}"
                valid_draws.append((draw_num, full_url))
            else:
                print(f"[=] Skipped existing draw {draw_num}")
    except Exception as e:
        print(f"[!] Decode error for value: {val} → {e}")

# Write URLs if any new draws found
if valid_draws:
    with open(URLS_OUTPUT_PATH, "w", encoding="utf-8") as f:
        for draw_num, url in valid_draws:
            f.write(url + "\n")
    print(f"[✓] Found {len(valid_draws)} valid draws on Singapore Pools site")
    print(f"[✓] {len(valid_draws)} new draw URLs written to {URLS_OUTPUT_PATH}")
    print(f"[DEBUG] First 3 new draws:")
    for draw_num, url in valid_draws[:3]:
        print(f"  → {url}")
else:
    print("[✓] No new draws found. draw_urls.txt not updated.")
