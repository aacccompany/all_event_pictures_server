from fastapi import APIRouter, Depends
from schemas.event import EventResponse, EventCreate
from sqlalchemy.orm import Session
from core.database import get_db
from services.event import EventService, EventUpdate
from typing import Annotated, List
from schemas.auth import UserResponse
from middleware.auth import get_current_admin
from datetime import datetime


from middleware.auth import get_current_admin, get_current_active_user

router = APIRouter()


@router.post("/event", response_model=EventResponse)
async def create_event(
    event: EventCreate,
    user: Annotated[UserResponse, Depends(get_current_admin)],
    db: Session = Depends(get_db),
):
    return EventService(db).create_event(event, user)


@router.get("/events", response_model=List[EventResponse])
async def get_events(db: Session = Depends(get_db), start_date: datetime = None, limit: int = None):
    return EventService(db).get_events(start_date, limit)


@router.get("/events/my-events", response_model=List[EventResponse])
async def get_my_events(
    user: Annotated[UserResponse, Depends(get_current_active_user)],
    db: Session = Depends(get_db), 
    start_date: datetime = None, 
    limit: int = None
):
    return EventService(db).get_my_events(user, start_date, limit)


@router.get("/events/my-created-events", response_model=List[EventResponse])
async def get_my_created_events(
    user: Annotated[UserResponse, Depends(get_current_admin)],
    db: Session = Depends(get_db), 
    start_date: datetime = None, 
    limit: int = None
):
    return EventService(db).get_my_created_events(user, start_date, limit)


@router.get("/event/{event_id}", response_model=EventResponse)
async def get_event(event_id: int, db: Session = Depends(get_db)):
    return EventService(db).get_event(event_id)


@router.patch("/event/{event_id}", response_model=EventResponse)
async def update_event(
    event_id: int,
    event: EventUpdate,
    user: Annotated[UserResponse, Depends(get_current_admin)],
    db: Session = Depends(get_db),
):
    return EventService(db).update_event(event_id, event, user)


@router.delete("/event/{event_id}")
async def remove_event(
    event_id: int,
    _: Annotated[UserResponse, Depends(get_current_admin)],
    db: Session = Depends(get_db),
):
    return EventService(db).remove_event(event_id)


@router.get("/search-events", response_model=List[EventResponse])
async def search_events(title: str, db: Session = Depends(get_db)):
    return EventService(db).search_events(title)


@router.get("/active-events", response_model=List[EventResponse])
async def get_active_events(db: Session = Depends(get_db)):
    return EventService(db).get_active_events()
