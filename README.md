
# 📊 Singapore Pools TOTO Scraper

Automated scraper for Singapore Pools TOTO draw results using Selenium and GitHub Actions.

Scrapes results from all historical draws (via dropdown), stores in structured JSON format, and updates nightly in batches.

---

## 📁 Repository Structure

```
.
├── docs/
│   └── toto_result.json        # Final accumulated results
├── draw_urls.txt              # Queue of upcoming draw pages to scrape
├── fetch_draw_links.py        # Detects new draw links from dropdown
├── selenium_scraper.py        # Scrapes result data from each draw page
└── .github/workflows/
    └── main.yml               # GitHub Actions workflow (runs daily)
```

---

## 🔄 Full Workflow

1. **Fetch draw list**  
   `fetch_draw_links.py` parses the dropdown menu from:

   ```
   https://www.singaporepools.com.sg/DataFileArchive/Lottery/Output/toto_result_draw_list_en.html
   ```

   ➤ Extracts draw numbers and sppl URLs  
   ➤ Compares against `docs/toto_result.json`  
   ➤ Writes new URLs to `draw_urls.txt` (if any)

2. **Run scraper**  
   `selenium_scraper.py`:
   - Loads top 50 URLs from `draw_urls.txt`
   - Opens them using headless Chrome + Selenium
   - Extracts date, draw number, winning/additional numbers, jackpot, and prize breakdowns
   - Appends new results to `toto_result.json`
   - Removes processed URLs from queue

3. **Push updates to GitHub**  
   If changes are made, GitHub Actions commits:
   - `docs/toto_result.json`
   - `draw_urls.txt` (if updated)

---

## ⏱ Automation Schedule

Configured in `.github/workflows/main.yml`:

```yaml
schedule:
  - cron: '0 12 * * *'  # 8:00 PM SGT
  - cron: '0 13 * * *'  # 9:00 PM SGT
  - cron: '0 14 * * *'  # 10:00 PM SGT
```

➡️ Each run processes **up to 50 new draws**  
➡️ Missed draws are automatically caught up on future runs

---

## ✅ Features

- Headless Chrome scraping via Selenium
- Draw queue batching with deduplication
- Output stored in clean, machine-readable JSON
- GitHub Actions handles all automation
- Incremental updates with auto-skip on duplicates

---

## 📦 Dependencies

In GitHub Actions:

```bash
pip install selenium beautifulsoup4 requests chromedriver-autoinstaller
```

---

## 📤 Output Format (`docs/toto_result.json`)

Each draw entry includes:

```json
{
  "date": "Mon, 14 Jul 2025",
  "draw_number": "4095",
  "winning_numbers": ["2", "8", "19", "29", "38", "41"],
  "additional_number": "20",
  "jackpot": "$5,792,345",
  "group_prizes": [
    { "group": "Group 1", "amount": "-", "shares": "-" },
    { "group": "Group 2", "amount": "$67,336", "shares": "9" }
  ]
}
```

---

## 📌 Notes

- `draw_urls.txt` acts as a temporary queue and is trimmed after each batch
- `fetch_draw_links.py` skips writing if no new draws found
- Idempotent: same draw is never scraped or saved twice

---
 
Built with ❤️ using Python, Selenium, and GitHub Actions.
