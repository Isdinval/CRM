import pytest
import pandas as pd
from backend.scripts.services.dedup import dedup

def test_exact_rpps_match():
    df = pd.DataFrame([
        {"rpps_number": "123", "last_name": "Dupont", "city": "Paris", "source": "ameli", "phone": "01"},
        {"rpps_number": "123", "last_name": "Dupont", "city": "Paris", "source": "doctolib", "website_url": "http://test.fr"}
    ])
    result = dedup(df)
    assert len(result) == 1
    assert result.iloc[0]['source'] == "ameli"
    assert result.iloc[0]['website_url'] == "http://test.fr"

def test_fuzzy_match():
    df = pd.DataFrame([
        {"last_name": "Dupont", "first_name": "Jean", "city": "Paris", "source": "ameli"},
        {"last_name": "Dupondt", "first_name": "Jean", "city": "Paris", "source": "doctolib"}
    ])
    result = dedup(df)
    assert len(result) == 1

def test_no_match():
    df = pd.DataFrame([
        {"last_name": "Dupont", "first_name": "Jean", "city": "Paris", "source": "ameli"},
        {"last_name": "Smith", "first_name": "John", "city": "Paris", "source": "ameli"}
    ])
    result = dedup(df)
    assert len(result) == 2

def test_phone_normalization():
    df = pd.DataFrame([
        {"phone": "01.02.03.04.05", "last_name": "A", "city": "C", "source": "ameli"},
        {"phone": "01 02 03 04 05", "last_name": "B", "city": "C", "source": "doctolib"}
    ])
    result = dedup(df)
    assert len(result) == 1
