"""
Database connection setup for the CleanMatch AI backend.

Uses SQLite for the MVP, as recommended in the project guide. Switching to
PostgreSQL/Supabase later only requires changing DATABASE_URL and the
connect_args below.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "sqlite:///./cleanmatch.db"

# check_same_thread=False is needed only for SQLite, since FastAPI may
# handle a request in a different thread than the one that created the
# connection.
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI dependency that yields a DB session and always closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
