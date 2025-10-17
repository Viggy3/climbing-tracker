from datetime import datetime
from pydantic import BaseModel, Field
from pymongo import MongoClient
class TrackerModel(BaseModel):
    id: str = Field(...)
    name: str = Field(...)
    description: str = Field(...)
    date: datetime = Field(default_factory=datetime.utcnow)
    attempts: int = Field(...)
    grade: str = Field(...)
    complete: bool = Field(default=False)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "unique_tracker_id",
                "name": "Climb Name",
                "description": "Description of the climb",
                "date": "2023-10-01T10:00:00",
                "attempts": 3,
                "grade": "5.10a",
                "complete": False
            }
        }

    