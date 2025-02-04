import os
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

router = APIRouter()

templates = Jinja2Templates(directory="src/template")


@router.get("/home", response_class=HTMLResponse)
async def read_home(request: Request):
    # print(f'PWD {os.path.dirname(os.path.realpath(__file__))}')
    return templates.TemplateResponse("home.html", {
        "request": request, "username": "TODO"})
