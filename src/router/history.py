from fastapi import APIRouter, Depends, Query, HTTPException
from src import schemas, history
from sqlalchemy.orm import Session
from src.database import SessionLocal
from typing import List, Optional

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/log", response_model=List[schemas.QueryLogResponse])
async def read_log(id: Optional[int] = Query(None), from_offset: Optional[int] = Query(0, alias="from"), db: Session = Depends(get_db)):
    if id is not None:
        log_entry = history.get_query_log(db, query_id=id)
        if not log_entry:
            raise HTTPException(status_code=404, detail="Query not found")
        return [log_entry]
    else:
        logs = history.get_query_logs(db, skip=from_offset)
        return logs
