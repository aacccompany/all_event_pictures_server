from pydantic import BaseModel
import datetime
from schemas.auth import UserResponse
from schemas.image import ImageResponse
from schemas.event_user import EventUserResponse

class Event(BaseModel):
    title: str 
    image_cover: str
    public_id:str
    date: datetime.date | None = None
    description: str | None = None
    location: str | None = None
    active: bool = False
    event_type: str
    limit: int | None = None
    joined_count: int | None = None
    # Price per image in satang (THB * 100)
    image_price: int | None = 2000
    
class EventCreate(Event):
    pass

class EventUpdate(Event):
    pass

class EventResponse(Event):
    id:int
    created_by: UserResponse
    images: list[ImageResponse]
    event_users: list[EventUserResponse]
    
    class Config:
        from_attributes = True
    