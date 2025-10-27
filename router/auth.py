from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
#adding template pointer
templates = Jinja2Templates(directory="templates")

auth = APIRouter(tags=["auth"])

@auth.get("/login")
async def login_redirect(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})
