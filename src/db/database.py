"""Connector class that also sets up the DB"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Example with SQLite; change to your production DB as needed.
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
