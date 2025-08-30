from fastapi import APIRouter, Depends
from schemas.event_user import EventUserResponse
from schemas.auth import UserResponse
from middleware.auth import get_current_user
from sqlalchemy.orm import Session
from core.database import get_db
from services.event_user import EventUserService
from schemas.event_user import EventUserJoin


router = APIRouter()

@router.post("/event/{event_id}/join", response_model=EventUserResponse)
async def join_event(event_id:int, user:UserResponse = Depends(get_current_user), db: Session = Depends(get_db)):
    return EventUserService(db).join_event(event_id, user.id)

@router.post("/event/{event_id}/invite", response_model=list[EventUserResponse])
async def invite_event(
    event_id: int,
    user: EventUserJoin,
    _: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return EventUserService(db).invite_events(event_id, user)


@router.delete("/event/{event_id}/leave")
async def leave_event(event_id:int, user:UserResponse = Depends(get_current_user), db:Session = Depends(get_db)):
    return EventUserService(db).leave_event(event_id, user.id)

