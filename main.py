from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from router.route import router
from router.auth import auth
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up Jinja2 templates
templates = Jinja2Templates(directory="templates")

# index route
@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Favicon route to prevent 404 errors
@app.get("/favicon.ico")
async def favicon():
    from fastapi.responses import Response
    return Response(status_code=204)  # No Content - tells browser no favicon available

# Redirect /login to /auth/login
@app.get("/login")
async def login_redirect():
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/auth/login", status_code=302)

# Include router with API prefix to avoid route conflicts
app.include_router(router, prefix="/api")

#Include router with login prefix
app.include_router(auth, prefix="/auth")

# Include CORS middleware

# Run the app with: uvicorn main:app --reload