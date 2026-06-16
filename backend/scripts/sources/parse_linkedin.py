import os
import pandas as pd

INPUT_FILE = "backend/scripts/data/linkedin_manual.csv"
OUTPUT_FILE = "backend/scripts/data/linkedin_raw.csv"

def parse():
    if not os.path.exists(INPUT_FILE):
        print(f"LinkedIn manual export not found at {INPUT_FILE}. Skipping.")
        return pd.DataFrame()

    print("Parsing LinkedIn manual export (Source 12)...")
    df = pd.read_csv(INPUT_FILE)

    # Expected columns: First Name, Last Name, Title, Company, Location, LinkedIn URL, Connections, Summary
    mapping = {
        'First Name': 'first_name',
        'Last Name': 'last_name',
        'LinkedIn URL': 'linkedin_url',
        'Connections': 'linkedin_followers',
        'Company': 'practice_name',
        'Location': 'location'
    }

    df = df.rename(columns=mapping)

    def parse_followers(val):
        if pd.isna(val): return 0
        val = str(val).replace('+', '').replace(',', '').replace(' ', '')
        try:
            return int(val)
        except:
            return 0

    if 'linkedin_followers' in df.columns:
        df['linkedin_followers'] = df['linkedin_followers'].apply(parse_followers)

    if 'location' in df.columns:
        # String split on ","
        df[['city', 'region']] = df['location'].str.split(',', n=1, expand=True)

    df['source'] = 'linkedin'
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"LinkedIn parse complete: {len(df)} rows.")
    return df

if __name__ == "__main__":
    parse()
