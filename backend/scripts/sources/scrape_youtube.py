import os
import requests
import pandas as pd
from dotenv import load_dotenv
from rapidfuzz import fuzz
import unicodedata
import re

load_dotenv()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
OUTPUT_FILE = "backend/scripts/data/youtube_raw.csv"

def normalize_name(s):
    if not isinstance(s, str): return ""
    s = "".join(c for c in unicodedata.normalize('NFKD', s) if not unicodedata.combining(c))
    s = s.lower()
    s = s.replace("dr", "").replace("docteur", "").strip()
    s = re.sub(r'[^\w\s]', '', s)
    return s

def fetch(merged_df: pd.DataFrame = None):
    if not YOUTUBE_API_KEY:
        print("YOUTUBE_API_KEY not set. Skipping YouTube scrape.")
        return pd.DataFrame()

    print("Starting YouTube channel matching (Source 9)...")

    queries = ["orthodontiste France", "orthodontie patient France", "Dr orthodontiste"]
    youtube_results = []

    for q in queries:
        url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            "part": "snippet",
            "type": "video",
            "q": q,
            "regionCode": "FR",
            "relevanceLanguage": "fr",
            "maxResults": 50,
            "key": YOUTUBE_API_KEY
        }
        try:
            res = requests.get(url, params=params)
            data = res.json()
            for item in data.get("items", []):
                snippet = item.get("snippet", {})
                youtube_results.append({
                    'channel_title': snippet.get('channelTitle'),
                    'description': snippet.get('description'),
                    'channel_url': f"https://www.youtube.com/channel/{snippet.get('channelId')}"
                })
        except Exception as e:
            print(f"Error fetching YouTube results for {q}: {e}")

    # Fuzzy match channel titles against known practitioner names
    if merged_df is not None and not merged_df.empty:
        matches = []
        for yt in youtube_results:
            yt_name = normalize_name(yt['channel_title'])
            for idx, row in merged_df.iterrows():
                p_name = normalize_name(f"{row.get('first_name', '')} {row.get('last_name', '')}")
                if p_name and fuzz.ratio(yt_name, p_name) >= 88:
                    matches.append({
                        'rpps_number': row.get('rpps_number'),
                        'email': row.get('email'),
                        'has_presented_webinar': True,
                        'source': 'youtube'
                    })

        df = pd.DataFrame(matches)
        df.to_csv(OUTPUT_FILE, index=False)
        return df

    return pd.DataFrame()

if __name__ == "__main__":
    fetch()
