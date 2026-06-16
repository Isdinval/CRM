import pandas as pd
from .dept_to_region import get_region

def infer_activity(followers):
    if pd.isna(followers) or followers <= 0:
        return "none"
    if followers <= 200:
        return "low"
    if followers <= 1000:
        return "medium"
    return "high"

def infer_website_quality(row):
    url = row.get('website_url')
    reviews = row.get('google_reviews_count', 0)
    if pd.isna(url) or not url:
        return "none"
    if not pd.isna(reviews) and reviews > 0:
        return "good"
    return "basic"

def infer_practice_type(num_practitioners):
    if pd.isna(num_practitioners) or num_practitioners <= 1:
        return "solo"
    if num_practitioners <= 4:
        return "group"
    return "clinic"

def enrich(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    df = df.copy()

    # Region inference
    if 'department' in df.columns:
        df['region'] = df['department'].apply(get_region)

    # LinkedIn activity inference
    if 'linkedin_followers' in df.columns:
        df['linkedin_activity'] = df['linkedin_followers'].apply(infer_activity)
    elif 'linkedin_activity' not in df.columns:
        df['linkedin_activity'] = "none"

    # Instagram activity inference
    if 'instagram_followers' in df.columns:
        df['instagram_activity'] = df['instagram_followers'].apply(infer_activity)
    elif 'instagram_activity' not in df.columns:
        df['instagram_activity'] = "none"

    if 'instagram_url' in df.columns:
        mask = df['instagram_url'].notna() & (df['instagram_url'] != "") & (df['instagram_activity'] == "none")
        df.loc[mask, 'instagram_activity'] = "low"

    # Website quality inference
    df['website_quality'] = df.apply(infer_website_quality, axis=1)

    # Practice type inference
    if 'num_practitioners' in df.columns:
        df['practice_type'] = df['num_practitioners'].apply(infer_practice_type)
    else:
        df['practice_type'] = "solo"
        df['num_practitioners'] = 1

    # Ensure lists for conferences and publications
    for col in ['conferences', 'publications']:
        if col not in df.columns:
            df[col] = [[] for _ in range(len(df))]
        else:
            df[col] = df[col].apply(lambda x: x if isinstance(x, list) else [])

    return df
