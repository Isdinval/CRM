import asyncio
from playwright.async_api import async_playwright
import requests
import pandas as pd
import os

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto("https://www.data.gouv.fr/fr/datasets/extraction-de-la-base-rpps/")
        await asyncio.sleep(5)
        # Find all download links
        links = await page.evaluate("() => Array.from(document.querySelectorAll('a[download]')).map(a => a.href)")
        print(f"Found download links: {links}")
        await browser.close()
        return links

if __name__ == "__main__":
    links = asyncio.run(run())
    if links:
        # Try downloading the first one
        target = links[0]
        res = requests.get(target)
        with open("backend/scripts/data/datagouv_raw.csv", "wb") as f:
            f.write(res.content)
