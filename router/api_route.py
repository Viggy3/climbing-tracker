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
from bson import ObjectId
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
        
        # Combine grade info with user notes
        if user_description:
            full_description = user_description
        else:
            full_description = "No additional notes."
            
        tracker_data = {
            "name": form_data.get("climb_name"),
            "description": full_description,
            "date": form_data.get("date"),
            "attempts": form_data.get("attempts", 1),  # Default to 1 attempt for new climb
            "grade": form_data.get("grade"),
            "complete": form_data.get("complete", False),  # Default to incomplete
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
        # Redirect to user dashboard
        return RedirectResponse(url="/user/my_tracker", status_code=302)
        
    except Exception as e:
        print(f" Error creating tracker: {e}")
        # Return to form with error
        return templates.TemplateResponse(
            "new_tracker.html", 
            {"request": request, "error": "Failed to create tracker. Please try again."}
        )

# Additional API routes can be added here
@api_router.get("/edit_tracker/{tracker_id}")
async def edit_tracker(tracker_id: str, request: Request):
    try:
        user_id = request.session.get('user_id')
        if not user_id:
            return RedirectResponse(url="/auth/login", status_code=302)
        from config.database import trackers_collection
        climb_data = trackers_collection.find_one({"_id": ObjectId(tracker_id), "user_id": user_id})
        if not climb_data:
            print(" Climb not found or access denied.") 
            return RedirectResponse(url="/user/my_tracker", status_code=302)
        context = {
            "request": request,
            "climb": climb_data
        }
        return templates.TemplateResponse("climb_details.html", context)
    except Exception as e:
        print(f" Error editing tracker: {e}")
        return RedirectResponse(url="/user/my_tracker", status_code=302)
    

@api_router.post("/update_tracker/{tracker_id}")
async def update_tracker(tracker_id: str, request: Request):
    try:
        form_data = await request.form()

        user_id = request.session.get('user_id')
        if not user_id:
            return RedirectResponse(url="/auth/login", status_code=302)
        from config.database import trackers_collection
        from datetime import datetime
        update_data = {
            "description": form_data.get("edit_climb_description", "").strip(),
            "attempts": int(form_data.get("edit_climb_attempts", 1)),
            "grade": form_data.get("edit_climb_grade"),
            "complete": form_data.get("edit_climb_complete") == "on"
        }
        print(form_data.items())
        trackers_collection.update_one(
            {"_id": ObjectId(tracker_id), "user_id": user_id},
            {"$set": update_data}
        )

        return RedirectResponse(url="/user/my_tracker", status_code=302)
    except Exception as e:
        print(f"error updating database climb {tracker_id}: {e}")
        return RedirectResponse(url="/user/my_tracker", status_code=302)
        # Convert date string to datetime if provided