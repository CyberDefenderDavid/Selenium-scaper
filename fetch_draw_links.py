import requests
from bs4 import BeautifulSoup
import os

DRAW_LIST_URL = "https://www.singaporepools.com.sg/DataFileArchive/Lottery/Output/toto_result_draw_list_en.html"
OUTPUT_FILE = "draw_urls.txt"

def fetch_draw_links():
    print("[+] Fetching draw list...")
    response = requests.get(DRAW_LIST_URL)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    options = soup.find_all("option")

    base_url = "https://www.singaporepools.com.sg/en/product/sr/Pages/toto_results.aspx?sppl="
    urls = []

    for opt in options:
        querystring = opt.get("querystring")
        if querystring:
            full_url = base_url + querystring  # FIXED: no extra "sppl="
            urls.append(full_url)

    if not urls:
        raise RuntimeError("[!] No draw links found. The source may have changed.")

    os.makedirs(os.path.dirname(OUTPUT_FILE) or ".", exist_ok=True)

    with open(OUTPUT_FILE, "w") as f:
        for url in urls:
            f.write(url + "\n")
        f.flush()
        os.fsync(f.fileno())

    print(f"[✓] {len(urls)} draw URLs written to {OUTPUT_FILE}")
    print("[DEBUG] First draw:", urls[0])
    print("[DEBUG] Last draw:", urls[-1])

if __name__ == "__main__":
    fetch_draw_links()
