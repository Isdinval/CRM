import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

OUTPUT_FILE = "backend/scripts/data/sante_dirs_raw.csv"

def scrape():
    print("Starting Santé directories scrape (Source 7)...")
    results = []

    # 7a. SantéNavigator
    try:
        res = requests.get("https://www.sante.fr/orthodontiste", timeout=10)
        soup = BeautifulSoup(res.text, 'lxml')
        # ... logic to parse static HTML ...
    except Exception as e:
        print(f"Error on SantéNavigator: {e}")

    # 7b. Medoucine
    try:
        res = requests.get("https://www.medoucine.com/orthodontiste", timeout=10)
        soup = BeautifulSoup(res.text, 'lxml')
        # ... logic to parse static HTML ...
    except Exception as e:
        print(f"Error on Medoucine: {e}")

    df = pd.DataFrame(results)
    df['source'] = 'sante_dirs'
    df.to_csv(OUTPUT_FILE, index=False)
    return df

if __name__ == "__main__":
    scrape()
