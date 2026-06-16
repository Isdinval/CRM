import os
import sys
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert
from tqdm import tqdm
import logging

# Add the parent directory to sys.path to import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.database import SessionLocal
from app.models.orthodontist import Orthodontist
from app.services.scoring import compute_score, get_tier

# Setup logging
os.makedirs("backend/scripts/logs", exist_ok=True)
logging.basicConfig(
    filename="backend/scripts/logs/import.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
warning_logger = logging.getLogger("dedup_warnings")
warning_handler = logging.FileHandler("backend/scripts/logs/dedup_warnings.log")
warning_logger.addHandler(warning_handler)

def import_dataframe(df: pd.DataFrame, dry_run: bool = False):
    if df.empty:
        print("No data to import.")
        return 0, 0, 0

    db = SessionLocal()
    new_count = 0
    updated_count = 0
    skipped_count = 0

    try:
        # Convert df to records
        records = df.to_dict('records')

        for record in tqdm(records, desc="Importing to DB"):
            # Clean record: remove NaNs, replace with None
            record = {k: (None if pd.isna(v) else v) for k, v in record.items()}

            # Compute score and tier
            score, _ = compute_score(record)
            record['prospect_score'] = score
            record['tier'] = get_tier(score, record.get('manual_tier_override'))

            if dry_run:
                new_count += 1 # Assume new for stats in dry run
                continue

            # Upsert logic
            rpps = record.get('rpps_number')
            email = record.get('email')

            stmt = None
            if rpps:
                stmt = insert(Orthodontist).values(**record)
                stmt = stmt.on_conflict_do_update(
                    index_elements=['rpps_number'],
                    set_={k: v for k, v in record.items() if k not in ['id', 'created_at', 'rpps_number']}
                ).returning(Orthodontist.id, (insert(Orthodontist).excluded.created_at == Orthodontist.created_at).label('is_new'))
            elif email:
                stmt = insert(Orthodontist).values(**record)
                stmt = stmt.on_conflict_do_update(
                    index_elements=['email'],
                    set_={k: v for k, v in record.items() if k not in ['id', 'created_at', 'email']}
                ).returning(Orthodontist.id, (insert(Orthodontist).excluded.created_at == Orthodontist.created_at).label('is_new'))
            else:
                # INSERT with warning
                warning_logger.warning(f"No RPPS or Email for: {record.get('last_name')} {record.get('first_name')} in {record.get('city')}. Source: {record.get('source')}")
                try:
                    obj = Orthodontist(**record)
                    db.add(obj)
                    db.flush()
                    new_count += 1
                except Exception as e:
                    logging.error(f"Error inserting record without RPPS/Email: {e}")
                    db.rollback()
                    skipped_count += 1
                continue

            if stmt is not None:
                try:
                    result = db.execute(stmt)
                    row = result.fetchone()
                    if row.is_new:
                        new_count += 1
                    else:
                        updated_count += 1
                except Exception as e:
                    logging.error(f"Error upserting record: {e}")
                    db.rollback()
                    skipped_count += 1

            # Batch commit every 100
            if (new_count + updated_count + skipped_count) % 100 == 0:
                db.commit()

        db.commit()
    finally:
        db.close()

    return new_count, updated_count, skipped_count
