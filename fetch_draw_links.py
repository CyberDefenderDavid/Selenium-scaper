import requests
import json
import base64
import os
from bs4 import BeautifulSoup

DRAW_PAGE = "https://www.singaporepools.com.sg/en/product/sr/Pages/toto_results.aspx"
RESULTS_JSON = "docs/toto_result.json"
DRAW_URLS_TXT = "draw_urls.txt"
BASE_URL = "https://www.singaporepools.com.sg/en/product/sr/Pages/toto_results.aspx?sppl="

def encode_draw_number(draw_number):
    return base64.b64encode(f"DrawNumber={draw_number}".encode("utf-8")).decode("utf-8")

def main():
    print("[+] Fetching draw list...")

    # Step 1: Load existing result draw_numbers and encode them
    try:
        with open(RESULTS_JSON, "r") as f:
            results = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        results = []

    encoded_existing = {encode_draw_number(entry["draw_number"]) for entry in results}
    print(f"[✓] Found {len(results)} results in {RESULTS_JSON}")

    # Step 2: Request dropdown content from Singapore Pools
    try:
        response = requests.get(DRAW_PAGE, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"[✗] Failed to fetch Singapore Pools page: {e}")
        return

    soup = BeautifulSoup(response.text, "html.parser")
    options = soup.select("select[id$='ddlPastDraws'] > option")
    print(f"[DEBUG] Total <option> tags found: {len(options)}")

    new_urls = []
    for opt in options:
        value = opt.get("value")
        text = opt.text.strip()

        if not value or not value.startswith("sppl="):
            continue

        encoded = value.split("=", 1)[1]
        try:
            decoded = base64.b64decode(encoded).decode("utf-8")
            draw_number = decoded.split("=", 1)[1]
        except Exception:
            print(f"[!] Failed to decode: {value}")
            continue

        print(f"[DEBUG] Option text: '{text}' | querystring: '{value}' | decoded: '{decoded}'")

        # Remove if already in results
        if encoded in encoded_existing:
            continue

        # Else add to new draw list
        full_url = f"{BASE_URL}{encoded}"
        new_urls.append(full_url)

    # Step 3: Write to draw_urls.txt if there are new URLs
    if new_urls:
        with open(DRAW_URLS_TXT, "w") as f:
            f.write("\n".join(new_urls))
        print(f"[✓] {len(new_urls)} new draw URLs written to {DRAW_URLS_TXT}")
        print("[DEBUG] First 3 new draws:")
        for url in new_urls[:3]:
            print(f"  → {url}")
    else:
        print("[✓] No new draws found. draw_urls.txt not updated.")

if __name__ == "__main__":
    main()
