from pydantic import BaseModel, ConfigDict
import datetime
from typing import List, Optional
from schemas.auth import UserResponse
from schemas.event_user import EventUserResponse

class Event(BaseModel):
    title: str
    image_cover: str
    public_id:str
    date: Optional[datetime.date] = None
    description: Optional[str] = None
    location: Optional[str] = None
    active: bool = False
    event_type: str
    limit: Optional[int] = None
    joined_count: Optional[int] = None
    # Price per image in satang (THB * 100)
    image_price: Optional[int] = 2000

class EventCreate(Event):
    pass

class EventUpdate(Event):
    pass

class EventBasic(Event):
    """Basic event info without nested relationships"""
    id: int
    created_by: UserResponse

    model_config = ConfigDict(from_attributes=True)

class EventResponse(Event):
    id:int
    created_by: UserResponse
    event_users: List[EventUserResponse]
    earnings: Optional[float] = 0.0
    sales_count: Optional[int] = 0
    # Images excluded to avoid circular import issues

    model_config = ConfigDict(from_attributes=True)
    