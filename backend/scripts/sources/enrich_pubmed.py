import requests
import pandas as pd
import time
import os

OUTPUT_FILE = "backend/scripts/data/pubmed_enriched.csv"

def fetch_publications(row):
    last_name = row.get('last_name')
    first_name = row.get('first_name')
    if not last_name or not first_name:
        return []

    query = f"{last_name} {first_name}[Author] AND orthodont*[Title/Abstract]"
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={query}&retmode=json&retmax=10"

    try:
        res = requests.get(url, timeout=5)
        data = res.json()
        count = int(data.get('esearchresult', {}).get('count', 0))
        if count > 0:
            ids = data.get('esearchresult', {}).get('idlist', [])
            # Fetch titles
            id_str = ",".join(ids)
            fetch_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={id_str}&rettype=title&retmode=text"
            titles_res = requests.get(fetch_url, timeout=5)
            titles = [t.strip() for t in titles_res.text.split('\n') if t.strip()]
            return titles
    except Exception as e:
        print(f"Error fetching PubMed for {last_name}: {e}")

    return []

def enrich(df: pd.DataFrame, top_n=500):
    print(f"Starting PubMed enrichment for top {top_n} prospects...")
    # Assume df is already scored and sorted
    top_prospects = df.head(top_n).copy()

    publications_col = []
    for idx, row in top_prospects.iterrows():
        titles = fetch_publications(row)
        publications_col.append(titles)
        # NCBI limit: 3 requests/second
        time.sleep(0.34)

    top_prospects['publications'] = publications_col

    # Merge back into original df
    df.loc[top_prospects.index, 'publications'] = top_prospects['publications']

    return df

if __name__ == "__main__":
    # Test
    dummy_df = pd.DataFrame([{'last_name': 'Dupont', 'first_name': 'Jean'}])
    enrich(dummy_df, top_n=1)
