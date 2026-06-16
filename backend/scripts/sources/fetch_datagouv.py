import os
import requests
import pandas as pd
from bs4 import BeautifulSoup
import zipfile
import io
import time
from datetime import datetime, timedelta

DATA_DIR = "backend/scripts/data"
OUTPUT_FILE = os.path.join(DATA_DIR, "datagouv_raw.csv")
DATASET_URL = "https://www.data.gouv.fr/fr/datasets/extraction-de-la-base-rpps/"

def should_download():
    if not os.path.exists(OUTPUT_FILE):
        return True

    file_time = datetime.fromtimestamp(os.path.getmtime(OUTPUT_FILE))
    if datetime.now() - file_time > timedelta(days=30):
        return True

    return False

def fetch():
    if not should_download():
        print("Data.gouv.fr file is recent, skipping download.")
        return pd.read_csv(OUTPUT_FILE)

    print("Fetching latest dataset from data.gouv.fr...")
    response = requests.get(DATASET_URL)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find links to CSV or ZIP files
    links = soup.find_all('a', href=True)
    target_link = None
    for link in links:
        href = link['href']
        if ('.csv' in href or '.zip' in href) and ('dentiste' in href.lower() or 'orthodontiste' in href.lower()):
            target_link = href
            break

    if not target_link:
        print("Could not find suitable dataset link on data.gouv.fr")
        return pd.DataFrame()

    print(f"Downloading from {target_link}...")
    res = requests.get(target_link)

    content = res.content
    if target_link.endswith('.zip'):
        with zipfile.ZipFile(io.BytesIO(content)) as z:
            # Find the largest CSV file in the zip
            csv_files = [f for f in z.namelist() if f.endswith('.csv')]
            csv_file = max(csv_files, key=lambda f: z.getinfo(f).file_size)
            with z.open(csv_file) as f:
                df = pd.read_csv(f, sep=None, engine='python', dtype=str)
    else:
        df = pd.read_csv(io.BytesIO(content), sep=None, engine='python', dtype=str)

    # Filtering and normalization
    # The columns might vary, we need to find the right ones
    # Common names: 'Libellé profession', 'Nom d'exercice', 'Prénom d'exercice', 'Identifiant PP', 'Commune d'exercice'

    # Column mapping based on typical RPPS extraction
    mapping = {
        'Identifiant PP': 'rpps_number',
        'Nom d\'exercice': 'last_name',
        'Prénom d\'exercice': 'first_name',
        'Libellé profession': 'profession',
        'Libellé Commune d\'exercice': 'city',
        'Code département d\'exercice': 'department',
        'Libellé Structure d\'exercice': 'practice_name',
        'Adresse e-mail d\'exercice': 'email',
        'Numéro de téléphone d\'exercice': 'phone',
        'Année d\'installation': 'installation_year'
    }

    # Try to find columns even if exact names differ slightly
    actual_mapping = {}
    for col in df.columns:
        for k, v in mapping.items():
            if k.lower() in col.lower():
                actual_mapping[col] = v
                break

    df = df.rename(columns=actual_mapping)

    # Filter for Orthodontistes
    if 'profession' in df.columns:
        df = df[df['profession'].str.contains('Orthodontiste', case=False, na=False)]

    df['source'] = 'datagouv'
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"Saved {len(df)} rows to {OUTPUT_FILE}")
    return df

if __name__ == "__main__":
    fetch()
