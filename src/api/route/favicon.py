"""FastApi route for favicon"""

import logging
import os
from logging import Logger

from fastapi import APIRouter
from fastapi.responses import FileResponse

logger: Logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/favicon.ico", response_class=FileResponse)
async def favicon() -> FileResponse:
    """favicon"""

    logger.debug("serving favicon...")
    return FileResponse(f"{os.getcwd()}/src/img/scarab-bnw.svg", media_type="image/svg+xml")
