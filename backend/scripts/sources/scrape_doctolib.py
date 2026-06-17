import asyncio
import os
import pandas as pd
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import random

OUTPUT_FILE = "backend/scripts/data/doctolib_raw.csv"

USER_AGENTS = [
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Mobile Safari/537.36"
]

async def scrape(headful=False):
    print("Starting Doctolib scrape (Source 4)...")
    results = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=not headful)
        context = await browser.new_context(user_agent=random.choice(USER_AGENTS))
        page = await context.new_page()

        url = "https://www.doctolib.fr/orthodontiste/paris" # Try a specific city to avoid global block
        print(f"Scraping Doctolib {url}...")

        try:
            await page.goto(url, wait_until="networkidle")
            await asyncio.sleep(5)

            content = await page.content()
            soup = BeautifulSoup(content, 'lxml')

            # Doctolib results are often in data attributes or specific classes
            names = soup.select('h3') # Very broad
            for name in names:
                if "Dr" in name.text:
                    results.append({
                        'last_name': name.text.replace("Dr", "").strip(),
                        'city': 'Paris',
                        'source': 'doctolib'
                    })

        except Exception as e:
            print(f"Error on Doctolib: {e}")

        await browser.close()

    df = pd.DataFrame(results)
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"Doctolib scrape complete: {len(results)} rows.")
    return df

if __name__ == "__main__":
    asyncio.run(scrape())
