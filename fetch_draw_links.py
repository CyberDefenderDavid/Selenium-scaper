import requests
from bs4 import BeautifulSoup
import json
import os

DRAW_LIST_URL = "https://www.singaporepools.com.sg/DataFileArchive/Lottery/Output/toto_result_draw_list_en.html"
RESULTS_FILE = "docs/toto_result.json"
OUTPUT_FILE = "draw_urls.txt"

def fetch_draw_links():
    print("[+] Fetching draw list...")
    res = requests.get(DRAW_LIST_URL)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "html.parser")

    options = soup.find_all("option")
    total_options = 0
    draws = []

    for opt in options:
        querystring = opt.get("querystring")
        text = opt.text.strip()
        if querystring and "Draw" in text:
            try:
                draw_number = text.split("Draw")[-1].strip()
                draws.append((draw_number, querystring))
                total_options += 1
            except Exception:
                continue

    print(f"[✓] Found {total_options} draws on Singapore Pools site")

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
    for draw_number, querystring in draws:
        if draw_number not in existing_draws:
            full_url = f"https://www.singaporepools.com.sg/en/product/sr/Pages/toto_results.aspx?sppl={querystring}"
            missing.append((int(draw_number), full_url))

    if not missing:
        print("[✓] All draws are already scraped.")
        return

    missing.sort(reverse=True)
    urls_only = [url for _, url in missing]

    with open(OUTPUT_FILE, "w") as f:
        for url in urls_only:
            f.write(url + "\n")
        f.flush()
        os.fsync(f.fileno())

    print(f"[✓] {len(missing)} draw URLs written to {OUTPUT_FILE}")
    print("[DEBUG] First 3 missing draws:")
    for url in urls_only[:3]:
        print("  →", url)

if __name__ == "__main__":
    fetch_draw_links()
