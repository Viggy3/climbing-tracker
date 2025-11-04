from fastapi import APIRouter, Request
from models.trackers import TrackerModel
from fastapi.responses import RedirectResponse
from config.database import trackers_collection as collection
from schema.schemas import individual_serial, list_serial
from bson import ObjectId
from fastapi.templating import Jinja2Templates
from schema.grade_utils import highest_grade

templates = Jinja2Templates(directory="templates")


user_router = APIRouter()

@user_router.get("/my_tracker")
async def get_my_tracker(request: Request, user_id: str = None, page_number: int = 1, per_page: int = 5):
    # Try to get user_id from session first, then from query parameter
    session_user_id = request.session.get('user_id')
    final_user_id = session_user_id or user_id
    
    if not final_user_id:
        # Redirect to login if no user authentication found
        return RedirectResponse(url="/auth/login")
    
    print(f"🔍 Searching for tracker with user_id: {final_user_id}")
    
    # Get single tracker for this user
    tracker = collection.find_one({"user_id": final_user_id})

    total_trackers_count = collection.count_documents({"user_id": final_user_id})
    total_pages = max(1, (total_trackers_count // per_page + 1))    
    page = max(1, min(page_number, total_pages))
    skip = (page - 1) * per_page

    # Get paginated trackers for this user
    paginated_trackers = list(
        collection.find(
            {"user_id": final_user_id}
        )
        .skip(skip)
        .sort("date", -1)
        .limit(per_page)
        )
    latest_tracker = paginated_trackers[0] if paginated_trackers else None

    # Get all trackers for this user (for stats)
    all_trackers = list(collection.find({"user_id": final_user_id}))

    highest_grade = "N/A"
    if all_trackers:
        grades = [t.get("grade", 0) for t in all_trackers if "grade" in t]
        highest_grade = max(grades) if grades else "N/A"
    
    # Prepare template context
    context = {
        "request": request,
        "tracker": individual_serial(tracker) if tracker else None,
        "all_trackers": [individual_serial(t) for t in all_trackers] if all_trackers else [],
        "user_id": final_user_id,
        "total_climbs": len(all_trackers),
        "completed_climbs": len([t for t in all_trackers if t.get("complete", False)]),
        "user_email": request.session.get('user_email', 'Not available'),
        "highest_grade": max([t.get("grade", 0) for t in all_trackers], default=0) if all_trackers else 0
    }
    
    print(f"✅ Found {len(all_trackers)} total trackers for user")
    return templates.TemplateResponse("dashboard.html", context)
    
    