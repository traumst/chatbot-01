from fastapi import APIRouter, Depends
from src import schemas, history
from sqlalchemy.orm import Session
from src.database import SessionLocal

router = APIRouter()

# Dependency to get DB session per request.


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/query", response_model=schemas.QueryLogResponse)
async def create_query(query: schemas.QueryLogCreate, db: Session = Depends(get_db)):
    # For demonstration, we simulate a response by reversing the query text.
    response_text = query.query_text[::-1]
    db_log = history.create_query_log(db, query, response_text=response_text)
    return db_log
