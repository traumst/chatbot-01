"""Web server exposing cached queries"""

import datetime

from typing import List, Optional

import uvicorn
from fastapi import FastAPI, Query, Request, Depends, HTTPException, APIRouter
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from src import history
from src.models import QueryLog
from src.schemas.query_request import QueryRequest
from src.schemas.query_response import QueryResponse
from src.middleware import get_db, validate_query
from src.utils.logger import logger
from src.utils.lru_cache import LRUCache

templates = Jinja2Templates(directory="src/template")
query_cache = LRUCache(size=100)

router = APIRouter()

def timestamp() -> str:
    return datetime.datetime.now().isoformat()

@router.post("/query", response_class=HTMLResponse)
async def create_query(
    request: Request,
    query_data: QueryRequest = Depends(validate_query),
    db: Session = Depends(get_db)
):
    """Simulate processing by reversing the query text"""
    logger.info(f"Received query from {request.client}: {query_data.query}")
    user_query: str = f"{query_data.query}"
    cached_response: Optional[QueryLog] = query_cache.get(user_query)
    if cached_response is None:
        print(f"New query will be cached: {user_query}")
        inverted_text: str = query_data.query[::-1]
        cached_response = history.create_query_log(db, query_data, response_text=inverted_text)
        query_cache.put(user_query, cached_response)
    else:
        print(f"Cached query response is served: {query_data.query}: {cached_response.response_text}")

    return templates.TemplateResponse("log_entry.html", {"request": request, "entry": cached_response})


@router.get("/home", response_class=HTMLResponse)
async def read_home(request: Request, db: Session = Depends(get_db)):
    """Home page, displaying past queries"""
    logger.info(f"Serving home to {request.client}")
    logs: List[QueryLog] = history.get_query_logs(db, skip=0, limit=10)

    return templates.TemplateResponse("home.html", {"request": request, "logs": logs})


@router.get("/log", response_model=List[QueryResponse])
async def read_log(
    request: Request,
    query_id: Optional[int] = Query(None),
    from_offset: Optional[int] = Query(0, alias="from"),
    db: Session = Depends(get_db)
) -> List[QueryLog]:
    """Get one or more queries from the log"""
    logger.info(f"Serving query log for {request.client}: query-{query_id}, offset-{from_offset}")
    logs: List[QueryLog]
    if query_id is not None:
        logs = [history.get_query_log(db, query_id=query_id)]
        if len(logs) == 0:
            raise HTTPException(status_code=404, detail="Query not found")
    elif from_offset is not None:
        logs = history.get_query_logs(db, skip=from_offset)
    else:
        logs = history.get_query_logs(db, skip=0, limit=10)

    return logs

app = FastAPI(title="LLM Query API", version="1.0")
app.include_router(router)
# Run the server (only if this script is run directly)
if __name__ == "__main__":
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=7654,
        proxy_headers=True,
        reload=True)
