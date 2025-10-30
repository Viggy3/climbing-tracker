from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional

class UserModel(BaseModel):
    id: Optional[str] = Field(None, description="Unique identifier (will be auto-generated)")
    email: str = Field(..., description="User's email address")
    name: str = Field(..., description="User's full name")
    google_sub: str = Field(..., description="Google's unique sub identifier for the user")
    refresh_token: Optional[str] = Field(None, description="OAuth2 refresh token")
    created_at: datetime = Field(default_factory=datetime.now, description="Account creation timestamp")
    token_expires_at: Optional[datetime] = Field(None, description="OAuth2 token expiration timestamp")
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "name": "John Doe",
                "google_sub": "12345678901234567890",
                "refresh_token": "1//0gLxyz...",
                "created_at": "2023-10-01T10:00:00",
                "token_expires_at": "2023-10-08T10:00:00",
                "last_login": "2023-10-05T15:30:00"
            }
        }

