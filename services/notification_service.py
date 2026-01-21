from sqlalchemy.orm import Session
from models.notification import NotificationDB
from typing import List

class NotificationService:
    def __init__(self, db: Session):
        self.db = db

    def create_notification(self, user_id: int, title: str, message: str) -> NotificationDB:
        notification = NotificationDB(
            user_id=user_id,
            title=title,
            message=message
        )
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        return notification

    def get_my_notifications(self, user_id: int) -> List[NotificationDB]:
        return self.db.query(NotificationDB).filter(
            NotificationDB.user_id == user_id
        ).order_by(NotificationDB.created_at.desc()).all()

    def mark_as_read(self, notification_id: int, user_id: int) -> NotificationDB:
        notification = self.db.query(NotificationDB).filter(
            NotificationDB.id == notification_id,
            NotificationDB.user_id == user_id
        ).first()
        
        if notification:
            notification.is_read = True
            self.db.commit()
            self.db.refresh(notification)
        
        return notification

    def get_unread_count(self, user_id: int) -> int:
        return self.db.query(NotificationDB).filter(
            NotificationDB.user_id == user_id,
            NotificationDB.is_read == False
        ).count()
