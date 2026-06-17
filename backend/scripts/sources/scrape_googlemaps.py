import os
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

SERPAPI_KEY = os.getenv("SERPAPI_KEY")
OUTPUT_FILE = "backend/scripts/data/googlemaps_raw.csv"

CITIES = [
    "Paris", "Marseille", "Lyon", "Toulouse", "Nice", "Nantes", "Montpellier",
    "Strasbourg", "Bordeaux", "Lille", "Rennes", "Reims", "Le Havre",
    "Saint-Étienne", "Toulon", "Grenoble", "Dijon", "Angers", "Nîmes", "Villeurbanne"
]

def fetch():
    if not SERPAPI_KEY:
        print("SERPAPI_KEY not set. Skipping Google Maps scrape.")
        return pd.DataFrame()

    print("Starting Google Maps scrape via SerpAPI (Source 6)...")
    results = []

    for city in CITIES:
        print(f"Fetching Google Maps for {city}...")
        for start in [0, 20]: # Get 2 pages
            params = {
                "engine": "google_maps",
                "q": f"orthodontiste {city}",
                "api_key": SERPAPI_KEY,
                "hl": "fr",
                "gl": "fr",
                "start": start
            }
            try:
                response = requests.get("https://serpapi.com/search.json", params=params)
                data = response.json()
                local_results = data.get("local_results", [])
                if not local_results:
                    break
                for place in local_results:
                    results.append({
                        'practice_name': place.get('title'),
                        'address': place.get('address'),
                        'phone': place.get('phone'),
                        'website_url': place.get('website'),
                        'google_reviews_count': place.get('reviews'),
                        'google_reviews_avg': place.get('rating'),
                        'city': city,
                        'source': 'googlemaps'
                    })
                if len(local_results) < 20:
                    break
            except Exception as e:
                print(f"Error fetching Google Maps for {city} at start {start}: {e}")
                break

    df = pd.DataFrame(results)
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"Google Maps scrape complete: {len(results)} rows.")
    return df

if __name__ == "__main__":
    fetch()
