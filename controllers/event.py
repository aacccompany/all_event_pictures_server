from fastapi import APIRouter, Depends
from schemas.event import EventResponse, EventCreate
from sqlalchemy.orm import Session
from core.database import get_db
from services.event import EventService
from typing import Annotated
from schemas.auth import UserResponse
from middleware.auth import get_current_admin

router = APIRouter()

@router.post("/event", response_model=EventResponse)
async def create_event(event: EventCreate, user:Annotated[UserResponse, Depends(get_current_admin)], db:Session = Depends(get_db)):
    return EventService(db).create_event(event, user) 
