import os
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import unquote
import re

BASE_URL = "https://www.singaporepools.com.sg/en/product/sr/Pages/toto_results.aspx"
RESULTS_FILE = "docs/toto_result.json"
URLS_FILE = "draw_urls.txt"

print("[+] Fetching draw list...")

response = requests.get(BASE_URL, timeout=10)
soup = BeautifulSoup(response.text, "html.parser")

# Find all option tags in the draw list
options = soup.select("select option")
print(f"[DEBUG] Total <option> tags found: {len(options)}")

draw_urls = []

# Load existing draw numbers from JSON
if os.path.exists(RESULTS_FILE):
    with open(RESULTS_FILE, "r", encoding="utf-8") as f:
        existing_data = json.load(f)
    existing_draws = {entry["draw_number"] for entry in existing_data}
else:
    existing_draws = set()

print(f"[✓] Found {len(existing_draws)} results in {RESULTS_FILE}")

# Extract and filter
valid_draws = 0
for option in options:
    text = option.get_text(strip=True)
    value = option.get("value", "")
    if not value.startswith("sppl="):
        continue

    sppl_raw = value
    sppl_decoded = unquote(sppl_raw)

    # Attempt to extract draw number from decoded value
    match = re.search(r"DrawNumber=0*(\d+)", sppl_decoded)
    if not match:
        continue

    draw_number = match.group(1)

    if draw_number in existing_draws:
        continue

    full_url = f"{BASE_URL}?{sppl_raw}"
    draw_urls.append(full_url)
    valid_draws += 1

if valid_draws == 0:
    print("[✓] No new draws found. draw_urls.txt not updated.")
else:
    with open(URLS_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(draw_urls))
    print(f"[✓] {valid_draws} new draw URLs written to {URLS_FILE}")
    print("[DEBUG] First 3 new draws:")
    for url in draw_urls[:3]:
        print(f"  → {url}")

print(f"[✓] Found {valid_draws} valid draws on Singapore Pools site")
