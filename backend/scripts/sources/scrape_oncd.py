import asyncio
import os
import pandas as pd
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import random
import logging

OUTPUT_FILE = "backend/scripts/data/oncd_raw.csv"
LOG_FILE = "backend/scripts/logs/scraping_errors.log"

os.makedirs("backend/scripts/logs", exist_ok=True)
logging.basicConfig(filename=LOG_FILE, level=logging.ERROR)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
]

async def scrape(headful=False):
    print("Starting ONCD scrape (Source 2)...")
    results = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=not headful)
        context = await browser.new_context(user_agent=random.choice(USER_AGENTS))
        page = await context.new_page()

        try:
            url = "https://www.conseil-national.medecin.fr/annuaire"
            await page.goto(url, wait_until="networkidle")

            # Check for captcha
            if await page.query_selector("iframe[src*='captcha']"):
                logging.error("Captcha detected on ONCD. Skipping source.")
                print("Captcha detected on ONCD. Skipping.")
                return pd.DataFrame()

            # Fill search: Orthodontiste
            # Note: This site often requires specific interaction
            await page.fill('input#recherche_profession', 'Chirurgien-dentiste spécialiste en orthopédie dento-faciale')
            await page.click('button#recherche_submit')
            await page.wait_for_load_state("networkidle")

            # Pagination logic...
            # For brevity in this exercise, we simulate extraction
            # results.append({...})

        except Exception as e:
            logging.error(f"Error on ONCD: {e}")
        finally:
            await browser.close()

    df = pd.DataFrame(results)
    df['source'] = 'oncd'
    df.to_csv(OUTPUT_FILE, index=False)
    return df

if __name__ == "__main__":
    asyncio.run(scrape())
