import json
import base64
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

TOTO_URL = "https://www.singaporepools.com.sg/en/product/sr/Pages/toto_results.aspx"
DRAW_URL_TEMPLATE = TOTO_URL + "?sppl={}"
RESULTS_JSON_PATH = "docs/toto_result.json"
DRAW_URLS_PATH = "draw_urls.txt"

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

def fetch_draw_options():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(TOTO_URL)
    time.sleep(5)  # Wait for JavaScript to render dropdown

    options = driver.find_elements(By.CSS_SELECTOR, "select[id$='ddlPastDraws'] > option")
    draw_data = []
    for opt in options:
        val = opt.get_attribute("value")
        text = opt.text.strip()
        if val:
            draw_data.append((val, text))
    driver.quit()
    return draw_data

def main():
    print("[+] Fetching draw list...")
    draw_options = fetch_draw_options()
    print(f"[DEBUG] Total <option> tags found: {len(draw_options)}")

    existing_draws = load_existing_draw_numbers(RESULTS_JSON_PATH)
    print(f"[✓] Found {len(draw_options)} valid draws on Singapore Pools site")
    print(f"[✓] Found {len(existing_draws)} results in {RESULTS_JSON_PATH}")

    new_urls = []
    for sppl_encoded, date_text in draw_options:
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
