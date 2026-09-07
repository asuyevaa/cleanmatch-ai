"""
Basic API tests. Run with `pytest` from the backend/ directory.

Uses a separate SQLite file (test.db) so tests never touch cleanmatch.db.
"""
import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

os.environ.setdefault("TESTING", "1")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import database.db as db_module
from database.db import Base, get_db

# --- point the app at a throwaway test database before importing main ---
TEST_DATABASE_URL = "sqlite:///./test.db"
test_engine = create_engine(
    TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


from main import app  # noqa: E402  (import after test DB setup)

app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_and_teardown_db():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


client = TestClient(app)

SAMPLE_HOUSEKEEPER = {
    "name": "Test Housekeeper",
    "services": ["deep_cleaning", "ironing"],
    "experience_years": 5,
    "service_area": "Ankara",
    "price_per_hour": 150.0,
    "pet_friendly": True,
    "availability": ["Saturday", "Sunday"],
    "bio": "Test profile",
}


def test_create_and_get_housekeeper():
    response = client.post("/housekeepers/", json=SAMPLE_HOUSEKEEPER)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Housekeeper"
    housekeeper_id = data["id"]

    get_response = client.get(f"/housekeepers/{housekeeper_id}")
    assert get_response.status_code == 200
    assert get_response.json()["service_area"] == "Ankara"


def test_get_nonexistent_housekeeper_returns_404():
    response = client.get("/housekeepers/9999")
    assert response.status_code == 404


def test_search_filters_by_service_and_pet_friendly():
    client.post("/housekeepers/", json=SAMPLE_HOUSEKEEPER)
    client.post(
        "/housekeepers/",
        json={**SAMPLE_HOUSEKEEPER, "name": "Other", "pet_friendly": False, "services": ["laundry"]},
    )

    response = client.get(
        "/housekeepers/search/",
        params={"service": "deep_cleaning", "pet_friendly": True},
    )
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 1
    assert results[0]["name"] == "Test Housekeeper"


def test_search_respects_max_price():
    client.post("/housekeepers/", json=SAMPLE_HOUSEKEEPER)  # price 150

    response = client.get("/housekeepers/search/", params={"max_price": 100})
    assert response.json() == []

    response = client.get("/housekeepers/search/", params={"max_price": 200})
    assert len(response.json()) == 1


def test_update_housekeeper_partial():
    create_response = client.post("/housekeepers/", json=SAMPLE_HOUSEKEEPER)
    housekeeper_id = create_response.json()["id"]

    update_response = client.put(
        f"/housekeepers/{housekeeper_id}", json={"price_per_hour": 175.0}
    )
    assert update_response.status_code == 200
    assert update_response.json()["price_per_hour"] == 175.0
    # untouched fields should remain the same
    assert update_response.json()["name"] == "Test Housekeeper"


def test_delete_housekeeper():
    create_response = client.post("/housekeepers/", json=SAMPLE_HOUSEKEEPER)
    housekeeper_id = create_response.json()["id"]

    delete_response = client.delete(f"/housekeepers/{housekeeper_id}")
    assert delete_response.status_code == 204

    get_response = client.get(f"/housekeepers/{housekeeper_id}")
    assert get_response.status_code == 404
