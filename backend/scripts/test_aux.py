import pandas as pd
from services.dept_to_region import get_region
from services.dedup import dedup
from services.enrich import enrich

def test_dept_to_region():
    assert get_region("75") == "Île-de-France"
    assert get_region("971") == "Guadeloupe"
    assert get_region("01") == "Auvergne-Rhône-Alpes"
    print("test_dept_to_region passed")

def test_enrich():
    df = pd.DataFrame([
        {"last_name": "Dupont", "first_name": "Jean", "city": "Paris", "department": "75", "linkedin_followers": 500, "website_url": "http://test.com", "google_reviews_count": 10},
        {"last_name": "Doe", "first_name": "Jane", "city": "Lyon", "department": "69", "instagram_url": "http://insta.com", "num_practitioners": 3}
    ])
    enriched = enrich(df)
    assert enriched.iloc[0]['region'] == "Île-de-France"
    assert enriched.iloc[0]['linkedin_activity'] == "medium"
    assert enriched.iloc[0]['website_quality'] == "good"
    assert enriched.iloc[1]['instagram_activity'] == "low"
    assert enriched.iloc[1]['practice_type'] == "group"
    print("test_enrich passed")

def test_dedup():
    df = pd.DataFrame([
        {"rpps_number": "123", "last_name": "Dupont", "first_name": "Jean", "city": "Paris", "source": "ameli", "phone": "0102030405"},
        {"rpps_number": "123", "last_name": "Dupont", "first_name": "J.", "city": "Paris", "source": "doctolib", "website_url": "http://dupont.fr"},
        {"last_name": "Doe", "first_name": "John", "city": "Marseille", "source": "ameli", "email": "john@doe.com"},
        {"last_name": "Doe", "first_name": "John", "city": "Marseille", "source": "oncd", "email": "john@doe.com", "phone": "0607080910"}
    ])
    deduped = dedup(df)
    assert len(deduped) == 2
    # Check if data merged
    dupont = deduped[deduped['last_name'] == "Dupont"].iloc[0]
    assert dupont['source'] == "ameli"
    assert dupont['website_url'] == "http://dupont.fr"

    doe = deduped[deduped['last_name'] == "Doe"].iloc[0]
    assert doe['phone'] == "0607080910"
    print("test_dedup passed")

if __name__ == "__main__":
    test_dept_to_region()
    test_enrich()
    test_dedup()
