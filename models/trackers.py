from datetime import datetime, timezone
from pydantic import BaseModel, Field
from typing import Optional

class TrackerModel(BaseModel):
    id: Optional[str] = Field(None, description="Unique identifier (will be auto-generated)")
    user_id: str = Field(..., description="ID of the user who owns this climb tracker")
    name: str = Field(...)
    description: str = Field(...)
    date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    attempts: int = Field(...)
    grade: str = Field(...)
    complete: bool = Field(default=False)
    media_ids: Optional[list[str]] = Field(None, description="List of associated media file IDs")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "507f1f77bcf86cd799439011",
                "name": "Climb Name",
                "description": "Description of the climb",
                "date": "2023-10-01T10:00:00",
                "attempts": 3,
                "grade": "5.10a", 
                "complete": False,
                "media_ids": ["607f1f77bcf86cd799439011", "607f1f77bcf86cd799439012"]
            }
        }