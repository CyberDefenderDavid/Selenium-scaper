import requests
from bs4 import BeautifulSoup
import json
import os
import re

DRAW_LIST_URL = "https://www.singaporepools.com.sg/DataFileArchive/Lottery/Output/toto_result_draw_list_en.html"
RESULTS_FILE = "docs/toto_result.json"
OUTPUT_FILE = "draw_urls.txt"

def fetch_draw_links():
    print("[+] Fetching draw list...")
    res = requests.get(DRAW_LIST_URL)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "html.parser")

    options = soup.find_all("option")
    print(f"[DEBUG] Total <option> tags found: {len(options)}")

    draws = []
    for opt in options:
        querystring = opt.get("querystring")
        text = opt.text.strip()
        if not querystring or not text:
            continue

        match = re.search(r'Draw\s+(\d+)', text)
        if match:
            draw_number = match.group(1)
            full_url = f"https://www.singaporepools.com.sg/en/product/sr/Pages/toto_results.aspx?sppl={querystring}"
            draws.append((draw_number, full_url))

    print(f"[✓] Found {len(draws)} valid draws on Singapore Pools site")

    existing_draws = set()
    if os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE, "r") as f:
            try:
                results = json.load(f)
                existing_draws = {entry["draw_number"] for entry in results}
            except Exception:
                pass

    print(f"[✓] Found {len(existing_draws)} results in {RESULTS_FILE}")

    missing = []
    for draw_number, url in draws:
        if draw_number not in existing_draws:
            missing.append((int(draw_number), url))

    if not missing:
        print(f"[✓] No new draws. Skipping update of {OUTPUT_FILE}")
        return

    missing.sort(reverse=True)
    urls_only = [url for _, url in missing]

    with open(OUTPUT_FILE, "w") as f:
        for url in urls_only:
            f.write(url + "\n")
        f.flush()
        os.fsync(f.fileno())

    print(f"[✓] {len(urls_only)} new draw URLs written to {OUTPUT_FILE}")
    print("[DEBUG] First 3 new draws:")
    for url in urls_only[:3]:
        print("  →", url)

if __name__ == "__main__":
    fetch_draw_links()
