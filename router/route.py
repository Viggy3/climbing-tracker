from fastapi import APIRouter
from models.trackers import TrackerModel
from config.database import collection
from schema.schemas import individual_serial, list_serial
from bson import ObjectId

router = APIRouter()

# GET request to fetch all trackers
@router.get("/")
async def get_all_trackers():
    trackers = list(collection.find())
    return list_serial(trackers)


#POST request to add a new tracker
@router.post("/")
async def add_tracker(tracker: TrackerModel):
    tracker_dict = tracker.model_dump()
    result = collection.insert_one(tracker_dict)
    new_tracker = collection.find_one({"_id": result.inserted_id})
    return individual_serial(new_tracker)
