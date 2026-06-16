import requests
from bs4 import BeautifulSoup
import pandas as pd
import pdfplumber
import io
import os
import re

OUTPUT_FILE = "backend/scripts/data/congres_raw.csv"

def extract_names_from_text(text):
    # Very simple regex for names: Dr. First Last or uppercase names
    # This would be much more sophisticated in reality
    names = re.findall(r'Dr\s+([A-Z][a-z]+\s+[A-Z][a-z]+)', text)
    return list(set(names))

def scrape():
    print("Starting Congrès scrape (Source 11)...")
    results = []

    urls = [
        "https://www.sfodf.org/congres",
        "https://www.orthodontie-francaise.fr"
    ]

    for url in urls:
        try:
            res = requests.get(url, timeout=10)
            soup = BeautifulSoup(res.text, 'lxml')

            # Look for PDF links
            for link in soup.find_all('a', href=True):
                if link['href'].endswith('.pdf'):
                    pdf_url = link['href']
                    if not pdf_url.startswith('http'):
                        pdf_url = os.path.join(url, pdf_url)

                    print(f"Downloading PDF: {pdf_url}")
                    pdf_res = requests.get(pdf_url)
                    with pdfplumber.open(io.BytesIO(pdf_res.content)) as pdf:
                        text = ""
                        for page in pdf.pages:
                            text += page.extract_text() or ""

                        found_names = extract_names_from_text(text)
                        for name in found_names:
                            parts = name.split(" ")
                            results.append({
                                'first_name': parts[0],
                                'last_name': parts[1],
                                'has_given_keynote': True,
                                'member_of_pro_association': True,
                                'pro_association_name': "SFODF" if "sfodf" in url else "SFO",
                                'source': 'congres'
                            })
        except Exception as e:
            print(f"Error scraping {url}: {e}")

    df = pd.DataFrame(results)
    df.to_csv(OUTPUT_FILE, index=False)
    return df

if __name__ == "__main__":
    scrape()
