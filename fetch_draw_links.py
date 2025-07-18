import requests
from bs4 import BeautifulSoup
import json
import os
import re
import base64

DRAW_LIST_URL = "https://www.singaporepools.com.sg/DataFileArchive/Lottery/Output/toto_result_draw_list_en.html"
RESULTS_FILE = "docs/toto_result.json"
OUTPUT_FILE = "draw_urls.txt"

def fetch_draw_links():
    print("[+] Fetching draw list...")
    try:
        res = requests.get(DRAW_LIST_URL)
        res.raise_for_status()
    except Exception as e:
        print(f"[✗] Failed to fetch draw list: {e}")
        return

    soup = BeautifulSoup(res.text, "html.parser")
    options = soup.find_all("option")
    print(f"[DEBUG] Total <option> tags found: {len(options)}")

    draws = []

    for opt in options:
        querystring = opt.get("querystring")
        text = opt.text.strip()

        if not querystring or not text:
            continue

        # Extract Base64 after 'sppl='
        encoded = querystring.split("=")[-1]
        try:
            decoded = base64.b64decode(encoded).decode("utf-8")
        except Exception:
            decoded = "(decode error)"

        print(f"[DEBUG] querystring: '{querystring}' | decoded: '{decoded}'")

        # Extract draw number from decoded string
        match = re.search(r"DrawNumber=(\d{4})", decoded)
        if not match:
            continue

        draw_number = match.group(1)
        full_url = f"https://www.singaporepools.com.sg/en/product/sr/Pages/toto_results.aspx?{querystring}"
        draws.append((draw_number, full_url))

    print(f"[✓] Found {len(draws)} valid draws on Singapore Pools site")

    # Load existing draw numbers from results.json
    existing_draws = set()
    if os.path.exists(RESULTS_FILE):
        try:
            with open(RESULTS_FILE, "r") as f:
                results = json.load(f)
                existing_draws = {entry["draw_number"] for entry in results}
        except Exception:
            print(f"[✗] Failed to parse {RESULTS_FILE}, continuing with empty set.")

    print(f"[✓] Found {len(existing_draws)} results in {RESULTS_FILE}")

    # Filter only new draw numbers
    missing = []
    for draw_number, url in draws:
        if draw_number not in existing_draws:
            missing.append((int(draw_number), url))

    if not missing:
        print(f"[✓] No new draws found. {OUTPUT_FILE} not updated.")
        return

    missing.sort(reverse=True)
    urls_only = [url for _, url in missing]

    try:
        with open(OUTPUT_FILE, "w") as f:
            for url in urls_only:
                f.write(url + "\n")
            f.flush()
            os.fsync(f.fileno())
    except Exception as e:
        print(f"[✗] Failed to write {OUTPUT_FILE}: {e}")
        return

    print(f"[✓] {len(urls_only)} new draw URLs written to {OUTPUT_FILE}")
    print("[DEBUG] First 3 new draws:")
    for url in urls_only[:3]:
        print("  →", url)

if __name__ == "__main__":
    fetch_draw_links()
