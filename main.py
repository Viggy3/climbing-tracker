from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles

from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
import os
from dotenv import load_dotenv
from config.database import users_collection as users, trackers_collection as trackers
from pymongo import MongoClient
from contextlib import asynccontextmanager

load_dotenv()

#check for secret key in .env
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable is not set")


app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY, session_cookie="session", same_site="lax")
# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up Jinja2 templates
templates = Jinja2Templates(directory="templates")

@asynccontextmanager
async def lifespan(app: FastAPI ):
    client = MongoClient(os.getenv("MONGODB_URL"))
    db = client[os.getenv("DATABASE_NAME", "ClimbingApp")]


    print("Starting up the FastAPI application...")
    #index mongodb

    users.create_index([("email", 1)], unique=True, sparse=True)
    users.create_index([("google_sub", 1)], unique=True, sparse=True)
    trackers.create_index([("user_id", 1), ("date", -1)])
    print("✓ MongoDB indexes ensured.")

    #attach to app
    app.mongo_client = client
    app.database = db

    print("FastAPI application started.")

    try:
        yield
    finally:
        print("Shutting down the FastAPI application...")
        client.close()
        print("FastAPI application shut down.")



from router.route import router
from router.auth import auth
from router.user_routes import user_router
from router.api_route import api_router
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
app.include_router(api_router, prefix="/api")

#Include router with login prefix
app.include_router(auth, prefix="/auth")

app.include_router(user_router, prefix="/user")
# Include CORS middleware

# Run the app with: uvicorn main:app --reload