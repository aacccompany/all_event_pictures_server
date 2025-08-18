from pydantic import BaseModel
import datetime
from schemas.auth import UserResponse
from schemas.image import ImageResponse


class Event(BaseModel):
    title: str 
    image_cover: str
    public_id:str
    event_type: str
    date: datetime.date | None = None
    description: str | None = None
    location: str | None = None
    active: bool = False
    
class EventCreate(Event):
    pass

class EventUpdate(Event):
    pass

class EventResponse(Event):
    id:int
    created_by: UserResponse
    images: list[ImageResponse]
    
    class Config:
        from_attributes = True
    