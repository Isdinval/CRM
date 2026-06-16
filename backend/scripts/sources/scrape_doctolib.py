import asyncio
import os
import pandas as pd
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import random

OUTPUT_FILE = "backend/scripts/data/doctolib_raw.csv"

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
]

async def scrape(headful=False):
    print("Starting Doctolib scrape (Source 4)...")
    results = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=not headful)
        context = await browser.new_context(user_agent=random.choice(USER_AGENTS))
        page = await context.new_page()

        page_num = 1
        while True:
            url = f"https://www.doctolib.fr/orthodontiste/france?page={page_num}"
            print(f"Scraping Doctolib page {page_num}...")

            try:
                await page.goto(url, wait_until="networkidle")

                # Check if page is empty or 404
                if "Aucun résultat" in await page.content():
                    break

                content = await page.content()
                soup = BeautifulSoup(content, 'lxml')

                items = soup.select('.dl-search-result')
                if not items:
                    break

                for item in items:
                    name_tag = item.select_one('.dl-search-result-name')
                    name_text = name_tag.text.strip() if name_tag else ""
                    # Split name if possible (Dr Jean Dupont)
                    parts = name_text.replace("Dr ", "").split(" ")
                    last_name = parts[-1] if parts else ""
                    first_name = " ".join(parts[:-1]) if len(parts) > 1 else ""

                    city_tag = item.select_one('.dl-text-body')
                    city = city_tag.text.strip() if city_tag else ""

                    reviews_tag = item.select_one('.dl-search-result-reviews')
                    # Expecting something like "4.8 (120 avis)"
                    reviews_text = reviews_tag.text.strip() if reviews_tag else ""

                    results.append({
                        'last_name': last_name,
                        'first_name': first_name,
                        'city': city,
                        'source': 'doctolib'
                    })

                page_num += 1
                await asyncio.sleep(random.uniform(2, 4))

            except Exception as e:
                print(f"Error on Doctolib page {page_num}: {e}")
                break

        await browser.close()

    df = pd.DataFrame(results)
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"Doctolib scrape complete: {len(results)} rows.")
    return df

if __name__ == "__main__":
    asyncio.run(scrape())
