import token
import os
from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.config import Config
from authlib.integrations.starlette_client import OAuth
from starlette.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from pathlib import Path
from config.database import users_collection, update_user_login, check_user_exists

#adding template pointer
templates = Jinja2Templates(directory="templates")

auth = APIRouter(tags=["auth"])

# Get the project root directory (parent of router folder)
PROJECT_ROOT = Path(__file__).parent.parent
config = Config(PROJECT_ROOT / ".env")

# Get BASE_URL from environment
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

oauth = OAuth(config)
oauth.register(
    name='google',
    client_id=config('GOOGLE_CLIENT_ID'),
    client_secret=config('GOOGLE_CLIENT_SECRET'),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    },
    redirect_uri=f'{BASE_URL}/auth/google/callback'
)

@auth.get("/login")
async def login_redirect(request: Request):
    return RedirectResponse(url="/auth/google/login")

@auth.get("/google/login")
async def google_login(request: Request):
    redirect_uri = f'{BASE_URL}/auth/google/callback'
    return await oauth.google.authorize_redirect(request, redirect_uri,  prompt='consent')

@auth.get("/google/callback")
async def google_callback(request: Request):
    try:
        token = await oauth.google.authorize_access_token(request)
        # Here you can handle the user information (e.g., create a session, store in DB, etc.)
        print(f"User info: {token['userinfo']}")
        print(f"Token info: {token}")
        print(f"Token keys: {token.keys()}")
        user_info = token['userinfo']
        # check if the user already exists
        existing_user = check_user_exists(user_info)
        if existing_user:
            print("User already exists. Logging in...")
            # Update last_login timestamp or any other info if needed
            update_user_login(existing_user['_id'])
            new_user_id = str(existing_user["_id"])
        else:
            print("New user. Creating user in database...")
            from datetime import datetime, timezone, timezone
            new_user = {
                "google_sub": user_info.get("sub"),
                "email": user_info.get("email"),
                "name": user_info.get("name"),
                "profile_pic": user_info.get("picture"),
                "created_at": datetime.now(timezone.utc),
                "last_login": datetime.now(timezone.utc)
            }
            result = users_collection.insert_one(new_user)
            new_user_id = str(result.inserted_id)  # Fixed: get ID from insert result
            print(f"New user created with ID: {new_user_id}")

        # Store user info in session (more secure than URL)
        request.session['user_id'] = new_user_id
        request.session['user_email'] = user_info.get("email")
        request.session['user_name'] = user_info.get("name")
        return RedirectResponse(url="/user/my_tracker")
    except Exception as e:
        print(f"Error occurred: {e}")
        return RedirectResponse(url="/login")

@auth.get("/logout")
async def logout(request: Request):
    try:
        request.session.clear()
        return RedirectResponse(url="/")
    except Exception as e:
        print(f"Error occurred: {e}")
        return RedirectResponse(url="/")