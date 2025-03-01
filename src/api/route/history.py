"""The log of previous queries and respective responses"""

import logging
from logging import Logger
from typing import Optional

from fastapi import Request, Depends, APIRouter, Query, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

import src.api.middleware.db_session as db_middleware
from src.db.tables import ask_record

templates = Jinja2Templates(directory="src/template")

logger: Logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/log", response_class=HTMLResponse)
async def history(
    request: Request,
    db_session: Session = Depends(db_middleware.get_db_session),
    query_id: Optional[int] = Query(0, alias="id", ge=1),
) -> HTMLResponse:
    """Get one or more queries from the log"""

    logger.info("Serving query id=%s for %s:%d", query_id, request.client.host, request.client.port)
    if query_id is None:
        raise ValueError("query_id is required")
    if isinstance(query_id, int) is False or query_id < 1:
        raise ValueError("query_id must be positive integer")
    query_log_record = ask_record.get_record(db_session, query_id=query_id)
    if query_log_record is None:
        raise HTTPException(
            status_code=555,
            detail="Query not found",
            headers={"Retry-After": "30"},
        )

    return templates.TemplateResponse(
        "ask_entry.j2", {
            "request": request,
            "entry": query_log_record,
        })
