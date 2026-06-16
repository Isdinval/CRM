import pandas as pd
import numpy as np
import unicodedata
import re
from rapidfuzz import fuzz

SOURCE_PRIORITY = {
    "ameli": 1,
    "datagouv": 2,
    "oncd": 3,
    "doctolib": 4,
    "googlemaps": 5,
    "linkedin": 6,
    "pagesjaunes": 7,
    "sante_dirs": 8,
    "medoucine": 9,
    "instagram_hints": 10,
    "youtube": 11,
    "pubmed": 12,
    "other": 99
}

def normalize_string(s):
    if not isinstance(s, str):
        return ""
    # Remove accents
    s = "".join(c for c in unicodedata.normalize('NFKD', s) if not unicodedata.combining(c))
    # Lowercase
    s = s.lower()
    # Strip punctuation and extra spaces
    s = re.sub(r'[^\w\s]', '', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def normalize_phone(p):
    if not isinstance(p, str):
        return ""
    # Strip spaces, dots, dashes
    return re.sub(r'[\s.\-]', '', p)

def is_empty(val):
    if pd.isna(val):
        return True
    if isinstance(val, str) and val == "":
        return True
    if isinstance(val, (list, np.ndarray)) and len(val) == 0:
        return True
    return False

def merge_rows(row1, row2):
    """Merge row2 into row1, favoring row1 for non-null fields or higher priority source."""
    p1 = SOURCE_PRIORITY.get(row1.get('source', 'other'), 99)
    p2 = SOURCE_PRIORITY.get(row2.get('source', 'other'), 99)

    # row1 should be the one with higher priority (lower number)
    if p2 < p1:
        row1, row2 = row2, row1

    merged = row1.copy()
    for col in row2.index:
        # Never overwrite a non-null field with a null
        if is_empty(merged.get(col)):
            if not is_empty(row2.get(col)):
                merged[col] = row2[col]

    return merged

def dedup(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    # Prepare for dedup
    df = df.copy()
    df['norm_name_city'] = df.apply(lambda r: normalize_string(f"{r.get('last_name', '')} {r.get('first_name', '')} {r.get('city', '')}"), axis=1)
    df['norm_phone'] = df['phone'].apply(normalize_phone) if 'phone' in df.columns else ""

    # Sort by priority and completeness
    df['priority'] = df['source'].map(lambda s: SOURCE_PRIORITY.get(s, 99))
    df['non_null_count'] = df.notnull().sum(axis=1)
    df = df.sort_values(by=['priority', 'non_null_count'], ascending=[True, False])

    initial_count = len(df)

    final_df = pd.DataFrame(columns=df.columns)
    remaining_df = df.copy()

    # Helper to process groups
    def process_groups(rem_df, group_col):
        if group_col not in rem_df.columns:
            return pd.DataFrame(columns=rem_df.columns), rem_df

        mask = rem_df[group_col].notnull() & (rem_df[group_col] != "")
        groups = rem_df[mask].groupby(group_col)
        deduped = []
        indices = set()
        for _, group in groups:
            merged = group.iloc[0]
            for i in range(1, len(group)):
                merged = merge_rows(merged, group.iloc[i])
            deduped.append(merged)
            indices.update(group.index)
        return pd.DataFrame(deduped, columns=rem_df.columns), rem_df.drop(index=list(indices))

    # Step 1: Exact match on rpps_number
    res, remaining_df = process_groups(remaining_df, 'rpps_number')
    final_df = pd.concat([final_df, res], ignore_index=True)

    # Step 2: Exact match on email
    res, remaining_df = process_groups(remaining_df, 'email')
    final_df = pd.concat([final_df, res], ignore_index=True)

    # Step 3: Exact match on phone
    res, remaining_df = process_groups(remaining_df, 'norm_phone')
    final_df = pd.concat([final_df, res], ignore_index=True)

    # Step 4: Exact match on name + city
    res, remaining_df = process_groups(remaining_df, 'norm_name_city')
    final_df = pd.concat([final_df, res], ignore_index=True)

    # Add what's left
    final_df = pd.concat([final_df, remaining_df], ignore_index=True)

    # Final pass for fuzzy match across the whole set
    final_df = final_df.sort_values(by=['priority', 'non_null_count'], ascending=[True, False])
    deduped_rows = []
    skip_indices = set()

    rows = final_df.to_dict('records')
    for i in range(len(rows)):
        if i in skip_indices:
            continue

        current_row = rows[i]
        for j in range(i + 1, len(rows)):
            if j in skip_indices:
                continue

            target_row = rows[j]
            # Use same city optimization if city exists and is not empty
            if current_row.get('city') and target_row.get('city') and current_row['city'] != target_row['city']:
                continue

            score = fuzz.token_sort_ratio(current_row['norm_name_city'], target_row['norm_name_city'])
            if score >= 92:
                # Merge target into current
                rows[i] = merge_rows(pd.Series(rows[i]), pd.Series(target_row)).to_dict()
                skip_indices.add(j)

        deduped_rows.append(rows[i])

    result_df = pd.DataFrame(deduped_rows)
    # Cleanup temporary columns
    cols_to_drop = ['norm_name_city', 'norm_phone', 'priority', 'non_null_count']
    result_df = result_df.drop(columns=[c for c in cols_to_drop if c in result_df.columns])

    print(f"Deduplication complete. Initial: {initial_count}, Final: {len(result_df)}")
    return result_df
