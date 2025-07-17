import os
import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import chromedriver_autoinstaller

URL_LIST_FILE = "draw_urls.txt"
OUTPUT_FILE = "docs/toto_result.json"
BATCH_SIZE = 50

# Ensure ChromeDriver is present
chromedriver_autoinstaller.install()

# Setup headless browser
options = Options()
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(options=options)

def scrape_draw(url):
    driver.get(url)
    time.sleep(3)

    block = driver.find_element(By.CLASS_NAME, "tables-wrap")

    date = block.find_element(By.CLASS_NAME, "drawDate").text.strip()
    draw_number = block.find_element(By.CLASS_NAME, "drawNumber").text.strip().replace("Draw No. ", "")
    winning_numbers = [td.text.strip() for td in block.find_elements(By.CSS_SELECTOR, "table:nth-of-type(2) tbody td")]
    additional_number = block.find_element(By.CSS_SELECTOR, "table:nth-of-type(3) .additional").text.strip()
    jackpot = block.find_element(By.CSS_SELECTOR, ".jackpotPrizeTable .jackpotPrize").text.strip()

    group_rows = block.find_elements(By.CSS_SELECTOR, ".tableWinningShares tbody tr")[1:]
    group_prizes = []
    for row in group_rows:
        cols = row.find_elements(By.TAG_NAME, "td")
        if len(cols) == 3:
            group_prizes.append({
                "group": cols[0].text.strip(),
                "amount": cols[1].text.strip(),
                "shares": cols[2].text.strip()
            })

    return {
        "date": date,
        "draw_number": draw_number,
        "winning_numbers": winning_numbers,
        "additional_number": additional_number,
        "jackpot": jackpot,
        "group_prizes": group_prizes
    }

def main():
    if not os.path.exists(URL_LIST_FILE):
        print(f"[!] {URL_LIST_FILE} not found.")
        return

    with open(URL_LIST_FILE, "r") as f:
        all_urls = [line.strip() for line in f if line.strip()]

    if not all_urls:
        print("[✓] No more URLs left to process.")
        return

    urls_to_process = all_urls[:BATCH_SIZE]
    remaining_urls = all_urls[BATCH_SIZE:]

    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, "r") as f:
            results = json.load(f)
    else:
        results = []

    existing_draws = {r["draw_number"] for r in results}
    added = 0

    for url in urls_to_process:
        try:
            result = scrape_draw(url)
            if result["draw_number"] not in existing_draws:
                results.append(result)
                print(f"[+] Added draw {result['draw_number']}")
                added += 1
            else:
                print(f"[=] Skipped existing draw {result['draw_number']}")
        except Exception as e:
            print(f"[!] Failed to scrape {url}: {e}")

    results.sort(key=lambda x: int(x["draw_number"]), reverse=True)

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w") as f:
        json.dump(results, f, indent=2)

    with open(URL_LIST_FILE, "w") as f:
        for url in remaining_urls:
            f.write(url + "\n")

    print(f"[✓] Batch complete: {added} added, {len(urls_to_process) - added} skipped.")

if __name__ == "__main__":
    main()
    driver.quit()
