from pydantic import BaseModel
from schemas.auth import UserResponse

class EventUserJoin(BaseModel):
    user_emails: list[str]


class EventUserResponse(BaseModel):
    id: int
    event_id: int
    user: UserResponse
    
    class Config:
        from_attributes = True
