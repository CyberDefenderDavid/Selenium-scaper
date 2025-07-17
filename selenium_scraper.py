from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time, json, os

URL = "https://www.singaporepools.com.sg/en/product/sr/Pages/toto_results.aspx?sppl="
OUTPUT_FILE = "docs/toto_result.json"

options = Options()
options.add_argument("--headless=new")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=options)

try:
    driver.get(URL)
    time.sleep(5)

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

    new_result = {
        "date": date,
        "draw_number": draw_number,
        "winning_numbers": winning_numbers,
        "additional_number": additional_number,
        "jackpot": jackpot,
        "group_prizes": group_prizes
    }

    os.makedirs("docs", exist_ok=True)

    existing = []
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, "r") as f:
            existing = json.load(f)

    if not any(d["draw_number"] == new_result["draw_number"] for d in existing):
        existing.append(new_result)
        existing.sort(key=lambda x: int(x["draw_number"]), reverse=True)
        with open(OUTPUT_FILE, "w") as f:
            json.dump(existing, f, indent=2)
        print(f"[+] Added draw {new_result['draw_number']}")
    else:
        print(f"[=] Draw {new_result['draw_number']} already exists")

finally:
    driver.quit()
