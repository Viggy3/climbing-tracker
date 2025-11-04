import token
from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.config import Config
from authlib.integrations.starlette_client import OAuth
from starlette.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from pathlib import Path
from config.database import users_collection, update_user_login, check_user_exists
import python_multipart
#adding template pointer
templates = Jinja2Templates(directory="templates")

api_router = APIRouter()

#display page for creating new tracker
@api_router.get("/new_tracker")
async def new_tracker_page(request: Request):
    return templates.TemplateResponse("new_tracker.html", {"request": request})

# POST request to add a new tracker
@api_router.post("/create_tracker")
async def create_tracker(request: Request):
    try:
        # Get form data instead of JSON
        form_data = await request.form()
        
        # Extract user_id from session
        user_id = request.session.get('user_id')
        if not user_id:
            return RedirectResponse(url="/auth/login", status_code=302)
        
        # Create tracker data from form
        user_description = form_data.get("description", "").strip()
        base_description = f"Grade: {form_data.get('grade')} ({form_data.get('grading_system')})"
        
        # Combine grade info with user notes
        full_description = base_description
        if user_description:
            full_description += f" - {user_description}"
            
        tracker_data = {
            "name": form_data.get("climb_name"),
            "description": full_description,
            "date": form_data.get("date"),
            "attempts": 1,  # Default to 1 attempt for new climb
            "grade": form_data.get("grade"),
            "complete": False,  # Default to incomplete
            "user_id": user_id  # Link to authenticated user
        }
        
        # Import here to avoid circular imports
        from config.database import trackers_collection
        from datetime import datetime
        
        # Convert date string to datetime if provided
        if tracker_data["date"]:
            tracker_data["date"] = datetime.fromisoformat(tracker_data["date"])
        else:
            tracker_data["date"] = datetime.utcnow()
        
        # Insert into database
        result = trackers_collection.insert_one(tracker_data)
        
        print(f"✅ Created new tracker: {tracker_data['name']} for user {user_id}")
        
        # Redirect to user dashboard
        return RedirectResponse(url="/user/my_tracker", status_code=302)
        
    except Exception as e:
        print(f"❌ Error creating tracker: {e}")
        # Return to form with error
        return templates.TemplateResponse(
            "new_tracker.html", 
            {"request": request, "error": "Failed to create tracker. Please try again."}
        )