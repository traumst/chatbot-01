"""Web server exposing cached queries"""

import datetime
import logging
from typing import List, Optional

import uvicorn
from fastapi import FastAPI, Query, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from src import history
from src.models import QueryLog
from src.schemas.query_request import QueryRequest
from src.schemas.query_response import QueryResponse
from src.middleware import get_db, validate_query

timestamp = datetime.datetime.now().isoformat()

log = logging.getLogger(__name__)
logging.basicConfig(
    filename='server.log',
    level=logging.INFO)
log.warning("Logging enabled with level %s", log.level)

app = FastAPI(title="LLM Query API", version="1.0")
templates = Jinja2Templates(directory="src/template")

@app.post("/query", response_class=HTMLResponse)
async def create_query(
    request: Request,
    query_data: QueryRequest = Depends(validate_query),
    db: Session = Depends(get_db)
):
    """Simulate processing by reversing the query text"""

    response_text = query_data.query[::-1]
    db_log = history.create_query_log(
        db, query_data, response_text=response_text)

    return templates.TemplateResponse("log_entry.html", {"request": request, "entry": db_log})


@app.get("/home", response_class=HTMLResponse)
async def read_home(request: Request, db: Session = Depends(get_db)):
    """Home page, displaying past queries"""

    logs: List[QueryLog] = history.get_query_logs(db, skip=0, limit=10)

    return templates.TemplateResponse("home.html", {"request": request, "logs": logs})


@app.get("/log", response_model=List[QueryResponse])
async def read_log(
    query_id: Optional[int] = Query(None),
    from_offset: Optional[int] = Query(0, alias="from"),
    db: Session = Depends(get_db)
) -> List[QueryLog]:
    """Get one or more queries from the log"""

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

# Run the server (only if this script is run directly)
if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=7654, reload=True)
