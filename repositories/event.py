from sqlalchemy.orm import Session
from models.event import EventDB
from schemas.event import EventCreate, EventUpdate
from schemas.auth import UserResponse
from datetime import datetime, timezone

class EventRepository:
    def __init__(self, db=Session):
        self.db = db

    def create(self, event: EventCreate, user: UserResponse):
        db_event = EventDB(**event.model_dump(), created_by_id=user.id, updated_by_id=user.id)
        self.db.add(db_event)
        self.db.commit()
        self.db.refresh(db_event)
        return db_event
    
    def get_all(self):
        return self.db.query(EventDB).filter(EventDB.deleted_at.is_(None)).all()
    
    def get_by_id(self, event_id:int):
        return self.db.query(EventDB).filter(EventDB.id == event_id, EventDB.deleted_at.is_(None)).first()
    
    def update(self, event_id:int, event:EventUpdate, user: UserResponse):
        db_event = self.get_by_id(event_id)
        if db_event:
            for key,value in event.model_dump().items():
                setattr(db_event, key, value)
            db_event.updated_by_id = user.id
            db_event.updated_at = datetime.now(timezone.utc)
            self.db.commit()
            self.db.refresh(db_event)
            return db_event
        
    def remove(self, event_id:int):
        db_event = self.get_by_id(event_id)
        if db_event:
            db_event.deleted_at = datetime.now(timezone.utc)
            self.db.commit()
            self.db.refresh(db_event)
            return db_event
        