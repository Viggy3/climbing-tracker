from datetime import datetime, timezone
from pydantic import BaseModel, Field
from typing import Optional

class TrackerModel(BaseModel):
    id: Optional[str] = Field(None, description="Unique identifier (will be auto-generated)")
    name: str = Field(...)
    description: str = Field(...)
    date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    attempts: int = Field(...)
    grade: str = Field(...)
    complete: bool = Field(default=False)

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Climb Name",
                "description": "Description of the climb",
                "date": "2023-10-01T10:00:00",
                "attempts": 3,
                "grade": "5.10a", 
                "complete": False
            }
        }