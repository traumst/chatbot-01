from sqlalchemy.orm import Session
from src import models, schemas


def create_query_log(db: Session, query_log: schemas.QueryLogCreate, response_text: str = None):
    db_log = models.QueryLog(
        query_text=query_log.query_text, response_text=response_text)
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log


def get_query_log(db: Session, query_id: int):
    return db.query(models.QueryLog).filter(models.QueryLog.id == query_id).first()


def get_query_logs(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.QueryLog).offset(skip).limit(limit).all()
