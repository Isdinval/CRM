import os
import sys
import argparse
import pandas as pd
import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import json

# Add current dir to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sources import fetch_datagouv, scrape_ameli, scrape_oncd, scrape_doctolib, scrape_pagesjaunes, \
                    scrape_googlemaps, scrape_sante_dirs, scrape_instagram_hints, scrape_youtube, \
                    enrich_pubmed, scrape_congres, parse_linkedin
from services.dedup import dedup
from services.enrich import enrich
from services.db_import import import_dataframe
from app.services.scoring import compute_score

def run_scrapers(selected_sources=None):
    print("Step 1: Running scrapers...")
    os.makedirs("backend/scripts/data", exist_ok=True)

    scrapers = {
        'datagouv': lambda: fetch_datagouv.fetch(),
        'ameli': lambda: asyncio.run(scrape_ameli.scrape()),
        'oncd': lambda: asyncio.run(scrape_oncd.scrape()),
        'doctolib': lambda: asyncio.run(scrape_doctolib.scrape()),
        'pagesjaunes': lambda: asyncio.run(scrape_pagesjaunes.scrape()),
        'googlemaps': lambda: scrape_googlemaps.fetch(),
        'sante_dirs': lambda: scrape_sante_dirs.scrape(),
        'instagram_hints': lambda: scrape_instagram_hints.fetch(),
        'congres': lambda: scrape_congres.scrape(),
        'linkedin': lambda: parse_linkedin.parse()
    }

    if selected_sources:
        scrapers = {k: v for k, v in scrapers.items() if k in selected_sources}

    results = {}
    with ThreadPoolExecutor(max_workers=3) as executor:
        future_to_source = {executor.submit(func): name for name, func in scrapers.items()}
        for future in future_to_source:
            source = future_to_source[future]
            try:
                df = future.result()
                results[source] = len(df) if df is not None else 0
            except Exception as e:
                print(f"Source {source} failed: {e}")
                results[source] = 0

    return results

def main():
    parser = argparse.ArgumentParser(description="SAYDO CRM Data Pipeline")
    parser.add_argument("--skip-scrape", action="store_true", help="Use existing CSVs, skip scrapers")
    parser.add_argument("--dry-run", action="store_true", help="Print stats only, no DB write")
    parser.add_argument("--enrich-pubmed", action="store_true", help="Run PubMed enrichment")
    parser.add_argument("--sources", type=str, help="Comma-separated list of sources to run")
    parser.add_argument("--headful", action="store_true", help="Run browsers in headful mode")

    args = parser.parse_args()

    report = {
        "timestamp": datetime.now().isoformat(),
        "sources": {}
    }

    selected_sources = args.sources.split(",") if args.sources else None

    # 1. Scraping
    if not args.skip_scrape:
        report["sources"] = run_scrapers(selected_sources)
    else:
        print("Skipping scraping, loading existing CSVs...")

    # 2. Merging
    print("Step 2: Merging data...")
    all_dfs = []
    data_dir = "backend/scripts/data"
    for filename in os.listdir(data_dir):
        if filename.endswith("_raw.csv"):
            df = pd.read_csv(os.path.join(data_dir, filename))
            if not df.empty:
                all_dfs.append(df)

    if not all_dfs:
        print("No data found to process.")
        return

    merged_raw = pd.concat(all_dfs, ignore_index=True)
    report["after_merge"] = len(merged_raw)
    merged_raw.to_csv(os.path.join(data_dir, "merged_raw.csv"), index=False)

    # 3. Deduplication
    print("Step 3: Deduplicating...")
    merged_deduped = dedup(merged_raw)
    report["after_dedup"] = len(merged_deduped)
    merged_deduped.to_csv(os.path.join(data_dir, "merged_deduped.csv"), index=False)

    # 4. Initial Enrichment
    print("Step 4: Enriching...")
    enriched = enrich(merged_deduped)

    # 5. YouTube matching (requires merged dataset in memory)
    yt_df = scrape_youtube.fetch(enriched)
    if yt_df is not None and not yt_df.empty:
        # Merge YouTube signals back
        # Since yt_df has rpps_number or email, we can merge on them
        for idx, row in yt_df.iterrows():
            if row.get('rpps_number'):
                mask = enriched['rpps_number'] == row['rpps_number']
                enriched.loc[mask, 'has_presented_webinar'] = True
            elif row.get('email'):
                mask = enriched['email'] == row['email']
                enriched.loc[mask, 'has_presented_webinar'] = True

    # 6. Initial Scoring (to find top 500 for PubMed)
    def calc_score(row):
        score, _ = compute_score(row.to_dict())
        return score

    enriched['prospect_score'] = enriched.apply(calc_score, axis=1)
    enriched = enriched.sort_values(by='prospect_score', ascending=False)

    # 7. PubMed Enrichment
    pubmed_count = 0
    if args.enrich_pubmed:
        enriched = enrich_pubmed.enrich(enriched, top_n=500)
        # Recalculate scores after PubMed
        enriched['prospect_score'] = enriched.apply(calc_score, axis=1)
        enriched = enriched.sort_values(by='prospect_score', ascending=False)
        # Count how many now have publications
        pubmed_count = enriched['publications'].apply(lambda x: len(x) > 0).sum()

    report["after_enrich"] = {
        "total": len(enriched),
        "pubmed_publications_added": pubmed_count
    }
    enriched.to_csv(os.path.join(data_dir, "enriched.csv"), index=False)

    # 8. DB Import
    print("Step 5: Importing to DB...")
    new, updated, skipped = import_dataframe(enriched, dry_run=args.dry_run)
    report["imported"] = {
        "new": new,
        "updated": updated,
        "skipped": skipped
    }

    # Export final CSV
    today = datetime.now().strftime("%Y-%m-%d")
    enriched.to_csv(os.path.join(data_dir, f"imported_{today}.csv"), index=False)

    # Summary
    print("\n--- Pipeline Summary ---")
    source_stats = ", ".join([f"{k}={v}" for k, v in report["sources"].items()])
    print(f"Sources: {source_stats}")
    print(f"After merge: {report['after_merge']}")
    print(f"After dedup: {report['after_dedup']}")
    print(f"After enrich: {report['after_enrich']['total']} (pubmed: {report['after_enrich']['pubmed_publications_added']} publications added)")
    print(f"Imported: {new + updated + skipped} (new: {new}, updated: {updated}, skipped: {skipped})")

    # Save report
    os.makedirs("backend/scripts/logs", exist_ok=True)
    report_file = f"backend/scripts/logs/import_report_{today}.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    print(f"Full report saved to {report_file}")

if __name__ == "__main__":
    main()
