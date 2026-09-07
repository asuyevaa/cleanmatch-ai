"""
CleanMatch AI backend entrypoint.

Stage covered here (see project guide, Stage 4): FastAPI backend + database
endpoints for housekeeper profiles, plus a basic /search endpoint. This
search endpoint is deliberately simple filtering logic for now — it is the
same function the agent's `search_housekeepers` tool will call in Stage 5,
so building it well now means the agent stage is mostly wiring, not new
logic.

Run locally with:
    uvicorn main:app --reload
"""
from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from database.db import Base, engine, get_db
from models.housekeeper import Housekeeper
from models.schemas import HousekeeperCreate, HousekeeperOut, HousekeeperUpdate

# Creates cleanmatch.db and the housekeepers table on first run.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="CleanMatch AI Backend",
    description="Agent-based housekeeping marketplace API (portfolio MVP).",
    version="0.1.0",
)


@app.get("/")
def root():
    return {"status": "ok", "service": "cleanmatch-ai-backend"}


# ---------------------------------------------------------------------
# CRUD endpoints
# ---------------------------------------------------------------------

@app.post("/housekeepers/", response_model=HousekeeperOut, status_code=201)
def create_housekeeper(payload: HousekeeperCreate, db: Session = Depends(get_db)):
    housekeeper = Housekeeper(**payload.model_dump())
    db.add(housekeeper)
    db.commit()
    db.refresh(housekeeper)
    return housekeeper


@app.get("/housekeepers/", response_model=List[HousekeeperOut])
def list_housekeepers(db: Session = Depends(get_db)):
    return db.query(Housekeeper).all()


@app.get("/housekeepers/{housekeeper_id}", response_model=HousekeeperOut)
def get_housekeeper(housekeeper_id: int, db: Session = Depends(get_db)):
    housekeeper = db.query(Housekeeper).filter(Housekeeper.id == housekeeper_id).first()
    if not housekeeper:
        raise HTTPException(status_code=404, detail="Housekeeper not found")
    return housekeeper


@app.put("/housekeepers/{housekeeper_id}", response_model=HousekeeperOut)
def update_housekeeper(
    housekeeper_id: int, payload: HousekeeperUpdate, db: Session = Depends(get_db)
):
    housekeeper = db.query(Housekeeper).filter(Housekeeper.id == housekeeper_id).first()
    if not housekeeper:
        raise HTTPException(status_code=404, detail="Housekeeper not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(housekeeper, field, value)

    db.commit()
    db.refresh(housekeeper)
    return housekeeper


@app.delete("/housekeepers/{housekeeper_id}", status_code=204)
def delete_housekeeper(housekeeper_id: int, db: Session = Depends(get_db)):
    housekeeper = db.query(Housekeeper).filter(Housekeeper.id == housekeeper_id).first()
    if not housekeeper:
        raise HTTPException(status_code=404, detail="Housekeeper not found")
    db.delete(housekeeper)
    db.commit()
    return None


# ---------------------------------------------------------------------
# Search endpoint — the DB-layer counterpart of the future
# search_housekeepers agent tool (project guide, Stage 5).
# ---------------------------------------------------------------------

@app.get("/housekeepers/search/", response_model=List[HousekeeperOut])
def search_housekeepers(
    service: Optional[str] = None,
    location: Optional[str] = None,
    pet_friendly: Optional[bool] = None,
    max_price: Optional[float] = None,
    day: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    Basic constraint filtering, matching the example in the project guide:
        location = Ankara, service = deep cleaning, pet_friendly = true,
        budget <= 2500

    This intentionally does NOT rank candidates — ranking is a separate,
    deterministic scoring step (calculate_match_score), kept out of this
    endpoint so each piece stays independently testable.
    """
    query = db.query(Housekeeper)

    if location:
        query = query.filter(Housekeeper.service_area.ilike(f"%{location}%"))
    if pet_friendly is not None:
        query = query.filter(Housekeeper.pet_friendly == pet_friendly)
    if max_price is not None:
        query = query.filter(Housekeeper.price_per_hour <= max_price)

    results = query.all()

    # services/availability are stored as JSON lists, so membership checks
    # (rather than SQL equality) happen in Python after the DB round-trip.
    if service:
        results = [h for h in results if service in (h.services or [])]
    if day:
        results = [h for h in results if day in (h.availability or [])]

    return results
