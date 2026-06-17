import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

OUTPUT_FILE = "backend/scripts/data/sante_dirs_raw.csv"

def scrape():
    print("Starting Santé directories scrape (Source 7)...")
    results = []

    cities = ["paris", "marseille", "lyon"]
    for city in cities:
        try:
            url = f"https://www.sante.fr/recherche/annuaire/orthodontiste/{city}"
            res = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
            soup = BeautifulSoup(res.text, 'lxml')

            # Simple parsing attempt
            for item in soup.select('.result-item'):
                name = item.select_one('.title').text.strip() if item.select_one('.title') else ""
                results.append({
                    'last_name': name,
                    'city': city.capitalize(),
                    'source': 'sante_dirs'
                })
        except Exception as e:
            print(f"Error on SantéNavigator for {city}: {e}")

    df = pd.DataFrame(results)
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"Santé directories scrape complete: {len(results)} rows.")
    return df

if __name__ == "__main__":
    scrape()
