from pydantic import BaseModel
import datetime
from schemas.auth import UserResponse


class Event(BaseModel):
    title: str 
    image_cover: str
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
    
    class Config:
        from_attributes = True
    