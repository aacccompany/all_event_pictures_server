from sqlalchemy.orm import Session
from models.event import EventDB
from schemas.event import EventCreate
from schemas.auth import UserResponse


class EventRepository:
    def __init__(self, db=Session):
        self.db = db

    def create(self, event: EventCreate, user: UserResponse):
        db_event = EventDB(**event.model_dump(), created_by_id=user.id, updated_by_id=user.id)
        self.db.add(db_event)
        self.db.commit()
        self.db.refresh(db_event)
        return db_event
