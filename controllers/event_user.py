from fastapi import APIRouter, Depends
from schemas.event_user import EventUserResponse
from schemas.auth import UserResponse
from middleware.auth import get_current_photographer, get_current_admin, get_current_active_user
from sqlalchemy.orm import Session
from core.database import get_db
from services.event_user import EventUserService
from schemas.event_user import EventUserJoin
from pydantic import BaseModel


class AddPhotographerRequest(BaseModel):
    user_id: int


router = APIRouter()

@router.post("/event/{event_id}/join", response_model=EventUserResponse)
async def join_event(event_id:int, user:UserResponse = Depends(get_current_photographer), db: Session = Depends(get_db)):
    return EventUserService(db).join_event(event_id, user.id)

@router.post("/event/{event_id}/invite", response_model=list[EventUserResponse])
async def invite_event(
    event_id: int,
    user: EventUserJoin,
    _: UserResponse = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    return EventUserService(db).invite_events(event_id, user)


@router.delete("/event/{event_id}/leave")
async def leave_event(event_id:int, user:UserResponse = Depends(get_current_photographer), db:Session = Depends(get_db)):
    return EventUserService(db).leave_event(event_id, user.id)


@router.get("/event/{event_id}/photographers", response_model=list[EventUserResponse])
async def get_event_photographers(
    event_id: int,
    current_user: UserResponse = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all photographers (users) joined to an event"""
    return EventUserService(db).get_event_photographers(event_id)


@router.post("/event/{event_id}/photographers", response_model=EventUserResponse)
async def add_photographer_to_event(
    event_id: int,
    request: AddPhotographerRequest,
    current_user: UserResponse = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Add a photographer (user) to an event. Event creator and admins can add photographers."""
    # Check if user is event creator or admin
    from repositories.event import EventRepository
    event = EventRepository(db).get_by_id(event_id)

    if not event:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")

    # Allow event creator, admin, or super-admin
    is_creator = event.created_by == current_user.id
    is_admin = current_user.role in ["admin", "super-admin"]

    if not is_creator and not is_admin:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only event creator and admins can add photographers"
        )

    return EventUserService(db).add_photographer_to_event(event_id, request.user_id)


@router.delete("/event/{event_id}/photographers/{user_id}")
async def remove_photographer_from_event(
    event_id: int,
    user_id: int,
    current_user: UserResponse = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Remove a photographer (user) from an event. Event creator and admins can remove photographers."""
    # Check if user is event creator or admin
    from repositories.event import EventRepository
    event = EventRepository(db).get_by_id(event_id)

    if not event:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")

    # Allow event creator, admin, or super-admin
    is_creator = event.created_by == current_user.id
    is_admin = current_user.role in ["admin", "super-admin"]

    if not is_creator and not is_admin:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only event creator and admins can remove photographers"
        )

    return EventUserService(db).remove_photographer_from_event(event_id, user_id)

