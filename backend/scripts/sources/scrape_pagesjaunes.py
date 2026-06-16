import asyncio
import os
import pandas as pd
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import random

OUTPUT_FILE = "backend/scripts/data/pagesjaunes_raw.csv"

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
]

async def scrape(headful=False):
    print("Starting Pages Jaunes scrape (Source 5)...")
    results = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=not headful)
        context = await browser.new_context(user_agent=random.choice(USER_AGENTS))
        page = await context.new_page()

        page_num = 1
        while True:
            url = f"https://www.pagesjaunes.fr/annuaire/chercherlespros?quoiqui=orthodontiste&ou=France&page={page_num}"
            print(f"Scraping Pages Jaunes page {page_num}...")

            try:
                await page.goto(url, wait_until="networkidle")

                content = await page.content()
                soup = BeautifulSoup(content, 'lxml')

                listings = soup.select('.bi-bloc')
                if not listings:
                    break

                for listing in listings:
                    practice_name = listing.select_one('.bi-denomination').text.strip() if listing.select_one('.bi-denomination') else ""
                    address = listing.select_one('.bi-address').text.strip() if listing.select_one('.bi-address') else ""
                    phone = listing.select_one('.num').text.strip() if listing.select_one('.num') else ""

                    results.append({
                        'practice_name': practice_name,
                        'address': address,
                        'phone': phone,
                        'source': 'pagesjaunes'
                    })

                page_num += 1
                await asyncio.sleep(random.uniform(2, 4))

                # Check for "Next" button to be sure
                if not await page.query_selector('a#pagination-next'):
                    break

            except Exception as e:
                print(f"Error on Pages Jaunes page {page_num}: {e}")
                break

        await browser.close()

    df = pd.DataFrame(results)
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"Pages Jaunes scrape complete: {len(results)} rows.")
    return df

if __name__ == "__main__":
    asyncio.run(scrape())
