"""
Populates the database with fictional housekeeper profiles for development
and demo purposes. Per the project guide's "Responsible matching" section,
these are synthetic profiles, not real people's data.

Run with:
    python -m sample_data.seed
(from inside the backend/ directory, with the venv active)
"""
import sys
from pathlib import Path

# Allow running this file directly as a script from backend/.
sys.path.append(str(Path(__file__).resolve().parent.parent))

from database.db import Base, SessionLocal, engine
from models.housekeeper import Housekeeper

SAMPLE_HOUSEKEEPERS = [
    dict(
        name="Ayşe Yılmaz",
        services=["deep_cleaning", "regular_cleaning", "ironing"],
        experience_years=7,
        service_area="Ankara - Çankaya",
        price_per_hour=180.0,
        pet_friendly=True,
        availability=["Tuesday", "Thursday", "Saturday"],
        bio="7 years of residential cleaning experience, specializes in deep cleaning.",
        cv_text=(
            "2017-2024: Independent housekeeper, Ankara. "
            "2015-2017: Housekeeping staff, Hilton Ankara."
        ),
    ),
    dict(
        name="Fatma Demir",
        services=["regular_cleaning", "laundry"],
        experience_years=3,
        service_area="Ankara - Keçiören",
        price_per_hour=140.0,
        pet_friendly=False,
        availability=["Monday", "Wednesday", "Friday"],
        bio="Reliable weekly cleaning, punctual and detail-oriented.",
        cv_text="2021-2024: Home cleaning services, Ankara.",
    ),
    dict(
        name="Zeynep Kaya",
        services=["deep_cleaning", "hotel_housekeeping", "ironing"],
        experience_years=10,
        service_area="Ankara - Yenimahalle",
        price_per_hour=220.0,
        pet_friendly=True,
        availability=["Saturday", "Sunday"],
        bio="Former hotel housekeeping supervisor, now freelance.",
        cv_text=(
            "2014-2024: Housekeeping Supervisor, Ankara HiltonSA. "
            "Certified in professional cleaning standards."
        ),
    ),
    dict(
        name="Elif Şahin",
        services=["regular_cleaning", "deep_cleaning"],
        experience_years=2,
        service_area="Ankara - Mamak",
        price_per_hour=120.0,
        pet_friendly=False,
        availability=["Tuesday", "Saturday"],
        bio="New to the platform, highly rated by early clients.",
        cv_text="2023-2024: Home cleaning, Ankara.",
    ),
    dict(
        name="Meryem Aydın",
        services=["deep_cleaning", "laundry", "ironing"],
        experience_years=5,
        service_area="Ankara - Etimesgut",
        price_per_hour=160.0,
        pet_friendly=True,
        availability=["Monday", "Thursday", "Saturday"],
        bio="Comfortable with pets, works well with families.",
        cv_text="2019-2024: Independent housekeeper, Ankara.",
    ),
    dict(
        name="Hatice Öztürk",
        services=["regular_cleaning", "ironing", "hotel_housekeeping"],
        experience_years=12,
        service_area="Ankara - Çankaya",
        price_per_hour=200.0,
        pet_friendly=False,
        availability=["Wednesday", "Friday", "Saturday"],
        bio="Over a decade of experience across homes and hotels.",
        cv_text="2012-2024: Housekeeping roles across three Ankara hotels.",
    ),
]


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(Housekeeper).count() > 0:
            print("Database already has housekeepers — skipping seed.")
            return
        for data in SAMPLE_HOUSEKEEPERS:
            db.add(Housekeeper(**data))
        db.commit()
        print(f"Seeded {len(SAMPLE_HOUSEKEEPERS)} synthetic housekeeper profiles.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
