from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from core.database import get_db
from middleware.auth import get_current_user_public, get_current_active_user
from schemas.auth import UserResponse
from schemas.notification import NotificationResponse
from services.notification_service import NotificationService
from typing import List

router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.get("/", response_model=List[NotificationResponse])
def get_my_notifications(
    user: UserResponse = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    service = NotificationService(db)
    return service.get_my_notifications(user.id)

@router.get("/unread-count")
def get_unread_count(
    user: UserResponse = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    service = NotificationService(db)
    return {"count": service.get_unread_count(user.id)}

@router.patch("/{id}/read")
def mark_read(
    id: int,
    user: UserResponse = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    service = NotificationService(db)
    return service.mark_as_read(id, user.id)
