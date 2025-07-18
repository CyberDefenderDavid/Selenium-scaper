import requests
from bs4 import BeautifulSoup
import base64
import json
import os
import re

DRAW_LIST_URL = "https://www.singaporepools.com.sg/DataFileArchive/Lottery/Output/toto_result_draw_list_en.html"
RESULTS_FILE = "docs/toto_result.json"
OUTPUT_FILE = "draw_urls.txt"

def decode_sppl(querystring):
    if not querystring or not querystring.startswith("sppl="):
        return None
    b64_value = querystring.split("=", 1)[-1]
    try:
        decoded = base64.b64decode(b64_value).decode("utf-8")
        return decoded
    except Exception:
        return None

def fetch_draw_links():
    print("[+] Fetching draw list...")

    try:
        res = requests.get(DRAW_LIST_URL)
        res.raise_for_status()
    except Exception as e:
        print(f"[ERROR] Failed to fetch draw list: {e}")
        return

    soup = BeautifulSoup(res.text, "html.parser")
    options = soup.find_all("option")
    print(f"[DEBUG] Total <option> tags found: {len(options)}")

    # Prepare draw entries with decoding
    raw_draws = []
    for opt in options:
        querystring = opt.get("querystring")
        text = opt.text.strip()

        if not querystring or not text:
            continue

        decoded = decode_sppl(querystring)
        if not decoded or "DrawNumber=" not in decoded:
            continue

        # Extract the actual 4-digit draw number from decoded string
        match = re.search(r"DrawNumber=(\d{4})", decoded)
        if not match:
            continue

        draw_number = match.group(1)
        full_url = f"https://www.singaporepools.com.sg/en/product/sr/Pages/toto_results.aspx?{querystring}"

        print(f"[DEBUG] querystring: '{querystring}' | decoded: '{decoded}'")
        raw_draws.append((draw_number, full_url))

    print(f"[✓] Found {len(raw_draws)} valid draws on Singapore Pools site")

    # Load existing draw results
    existing_draws = set()
    if os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE, "r") as f:
            try:
                results = json.load(f)
                existing_draws = {entry["draw_number"] for entry in results}
            except Exception:
                print("[WARN] Could not load or parse results file.")

    print(f"[✓] Found {len(existing_draws)} results in {RESULTS_FILE}")

    # Identify new draws
    new_draws = []
    for draw_number, url in raw_draws:
        if draw_number not in existing_draws:
            new_draws.append((int(draw_number), url))  # int for sorting

    if not new_draws:
        print(f"[✓] No new draws found. {OUTPUT_FILE} not updated.")
        return

    # Write sorted newest first
    new_draws.sort(reverse=True)
    urls_only = [url for _, url in new_draws]

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
