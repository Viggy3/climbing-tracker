from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from models.trackers import TrackerModel
from fastapi.responses import HTMLResponse, RedirectResponse
from config.database import trackers_collection as collection
from schema.grade_utils import highest_grade
from schema.schemas import individual_serial, list_serial
from bson import ObjectId

templates = Jinja2Templates(directory="templates")

router = APIRouter()

# GET request to fetch all trackers
@router.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    user_id = request.session.get('user_id')
    if not user_id:
        return templates.TemplateResponse("index.html", {"request": request, "user" : None})

    climbs = list(collection.find({"user_id": user_id}))
    completed = [c["grade"] for c in climbs if c.get("complete")]
    attempted = [c["grade"] for c in climbs if not c.get("complete")]

    recent = sorted(climbs, key=lambda x: x.get("date", 0), reverse=True)[:5]

    return templates.TemplateResponse("index.html", {
        "request": request,
        "user": {"user_id": user_id},
        "climbs": climbs,
        "completed_highest": highest_grade(completed),
        "total_completed": len(completed),
        "attempted_highest": highest_grade(attempted),
        "recent_climbs": recent
    })
