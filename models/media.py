from pydantic import BaseModel, Field
from bson import ObjectId
from datetime import datetime, timezone
from typing import Optional, Literal

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        if isinstance(v, ObjectId):
            return v
        try:
            return ObjectId(str(v))
        except Exception:
            raise ValueError("Not a valid ObjectId")


class MediaModel(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None, description="Unique identifier (will be auto-generated)")
    tracker_id: str = Field(..., description="Associated tracker ID")
    key: str = Field(..., description="Storage key or URL for the media file")
    filename: str = Field(..., description="Original filename of the media")
    mime: str = Field(..., description="MIME type of the media file")
    size: int = Field(..., description="Size of the media file in bytes")
    status: Literal["uploaded", "processing", "failed"] = Field("uploaded", description="Status of the media file")
    uploaded_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc), description="Timestamp of when the media was uploaded")


    class Config:
        json_schema_extra = {
            "example": {
                "tracker_id": "607f1f77bcf86cd799439011",
                "key": "media/607f1f77bcf86cd799439011/image1.png",
                "filename": "image1.png",
                "mime": "image/png",
                "size": 204800,
                "status": "uploaded",
                "uploaded_at": "2023-10-01T10:00:00"
            }
        }


