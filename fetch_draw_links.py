import json
import base64
from bs4 import BeautifulSoup
import requests

TOTO_URL = "https://www.singaporepools.com.sg/en/product/sr/Pages/toto_results.aspx"
DRAW_URL_TEMPLATE = TOTO_URL + "?sppl={}"
RESULTS_JSON_PATH = "docs/toto_result.json"
DRAW_URLS_PATH = "draw_urls.txt"

def fetch_draw_options():
    response = requests.get(TOTO_URL)
    soup = BeautifulSoup(response.text, "html.parser")
    return soup.select("select[id$='ddlPastDraws'] > option")

def decode_draw_number(sppl_encoded):
    try:
        decoded = base64.b64decode(sppl_encoded).decode("utf-8")
        if "DrawNumber=" in decoded:
            return int(decoded.split("DrawNumber=")[-1])
    except Exception:
        return None

def load_existing_draw_numbers(path):
    try:
        with open(path, "r") as f:
            return set(int(entry["draw_number"]) for entry in json.load(f))
    except Exception:
        return set()

def main():
    print("[+] Fetching draw list...")
    options = fetch_draw_options()
    print(f"[DEBUG] Total <option> tags found: {len(options)}")

    existing_draws = load_existing_draw_numbers(RESULTS_JSON_PATH)
    print(f"[✓] Found {len(options)} valid draws on Singapore Pools site")
    print(f"[✓] Found {len(existing_draws)} results in {RESULTS_JSON_PATH}")

    new_urls = []
    for opt in options:
        sppl_encoded = opt.get("value")
        draw_date = opt.text.strip()
        if not sppl_encoded:
            continue
        draw_number = decode_draw_number(sppl_encoded)
        if draw_number and draw_number not in existing_draws:
            full_url = DRAW_URL_TEMPLATE.format(sppl_encoded)
            new_urls.append(full_url)

    if new_urls:
        with open(DRAW_URLS_PATH, "w") as f:
            for url in new_urls:
                f.write(url + "\n")
        print(f"[✓] {len(new_urls)} new draw URLs written to {DRAW_URLS_PATH}")
        print("[DEBUG] First 3 new draws:")
        for url in new_urls[:3]:
            print(f"  → {url}")
    else:
        print("[✓] No new draws found. draw_urls.txt not updated.")

if __name__ == "__main__":
    main()
