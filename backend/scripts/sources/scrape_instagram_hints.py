import os
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

SERPAPI_KEY = os.getenv("SERPAPI_KEY")
OUTPUT_FILE = "backend/scripts/data/instagram_hints_raw.csv"

CITIES = [
    "Paris", "Marseille", "Lyon", "Toulouse", "Nice", "Nantes", "Montpellier",
    "Strasbourg", "Bordeaux", "Lille", "Rennes", "Reims", "Le Havre",
    "Saint-Étienne", "Toulon", "Grenoble", "Dijon", "Angers", "Nîmes", "Villeurbanne"
]

def fetch():
    if not SERPAPI_KEY:
        print("SERPAPI_KEY not set. Skipping Instagram hints scrape.")
        return pd.DataFrame()

    print("Starting Instagram hints scrape via SerpAPI (Source 8)...")
    results = []

    for city in CITIES:
        print(f"Fetching Instagram hints for {city}...")
        params = {
            "engine": "google",
            "q": f"orthodontiste site:instagram.com {city}",
            "api_key": SERPAPI_KEY,
            "num": 5,
            "hl": "fr",
            "gl": "fr"
        }

        try:
            response = requests.get("https://serpapi.com/search.json", params=params)
            data = response.json()

            for result in data.get("organic_results", []):
                results.append({
                    'instagram_url': result.get('link'),
                    'username': result.get('title'),
                    'city': city,
                    'source': 'instagram_hints'
                })
        except Exception as e:
            print(f"Error fetching Instagram hints for {city}: {e}")

    df = pd.DataFrame(results)
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"Instagram hints scrape complete: {len(results)} rows.")
    return df

if __name__ == "__main__":
    fetch()
