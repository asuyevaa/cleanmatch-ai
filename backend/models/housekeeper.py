"""
ORM model for housekeeper profiles.

Fields map directly to the profile concept in the project guide: skills,
experience, availability, service area, pricing, and CV text (which the
agent's read_cv tool will later turn into structured data).
"""
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, JSON, String

from database.db import Base


class Housekeeper(Base):
    __tablename__ = "housekeepers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)

    # e.g. ["deep_cleaning", "regular_cleaning", "ironing", "laundry",
    #       "hotel_housekeeping"]
    services = Column(JSON, nullable=False, default=list)

    experience_years = Column(Integer, nullable=False, default=0)

    # City / district, e.g. "Ankara" or "Ankara - Çankaya"
    service_area = Column(String, nullable=False)

    price_per_hour = Column(Float, nullable=False)

    pet_friendly = Column(Boolean, nullable=False, default=False)

    # Weekdays the housekeeper is generally available, e.g.
    # ["Monday", "Wednesday", "Saturday"]. A future iteration could move
    # this to a separate table with real date/time slots.
    availability = Column(JSON, nullable=False, default=list)

    bio = Column(String, nullable=True)

    # Raw CV text as uploaded/pasted. The read_cv agent tool will parse
    # this into structured fields; the housekeeper can review/edit the
    # result rather than trusting it blindly (see "Responsible matching"
    # in the project guide).
    cv_text = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
