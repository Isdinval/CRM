import pytest
import pandas as pd
from backend.scripts.services.enrich import enrich

def test_linkedin_activity_bands():
    df = pd.DataFrame([
        {"linkedin_followers": 0},
        {"linkedin_followers": 150},
        {"linkedin_followers": 500},
        {"linkedin_followers": 1500},
        {"linkedin_followers": None}
    ])
    result = enrich(df)
    assert result.iloc[0]['linkedin_activity'] == "none"
    assert result.iloc[1]['linkedin_activity'] == "low"
    assert result.iloc[2]['linkedin_activity'] == "medium"
    assert result.iloc[3]['linkedin_activity'] == "high"
    assert result.iloc[4]['linkedin_activity'] == "none"

def test_practice_type_inference():
    df = pd.DataFrame([
        {"num_practitioners": 1},
        {"num_practitioners": 3},
        {"num_practitioners": 10},
        {"num_practitioners": None}
    ])
    result = enrich(df)
    assert result.iloc[0]['practice_type'] == "solo"
    assert result.iloc[1]['practice_type'] == "group"
    assert result.iloc[2]['practice_type'] == "clinic"
    assert result.iloc[3]['practice_type'] == "solo"

def test_website_quality_inference():
    df = pd.DataFrame([
        {"website_url": "http://test.fr", "google_reviews_count": 10},
        {"website_url": "http://test.fr", "google_reviews_count": 0},
        {"website_url": None, "google_reviews_count": 50}
    ])
    result = enrich(df)
    assert result.iloc[0]['website_quality'] == "good"
    assert result.iloc[1]['website_quality'] == "basic"
    assert result.iloc[2]['website_quality'] == "none"

def test_non_overwrite_null():
    # This is more for dedup merge, but let's check basic enrich doesn't break things
    df = pd.DataFrame([{"last_name": "Test", "website_url": "existing"}])
    result = enrich(df)
    assert result.iloc[0]['website_url'] == "existing"
