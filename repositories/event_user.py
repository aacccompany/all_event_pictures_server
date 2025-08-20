from sqlalchemy.orm import Session
from models.event_user import EventUserDB


class EventUserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_event_user(self, event_id: int, user_id: int):
        return self.db.query(EventUserDB).filter(
            EventUserDB.event_id == event_id, EventUserDB.user_id == user_id).first()

    def add_user(self, event_id: int, user_id: int):
        db_event_user = EventUserDB(event_id=event_id, user_id=user_id)
        self.db.add(db_event_user)
        self.db.commit()
        self.db.refresh(db_event_user)
        return db_event_user
    
    def remove_event_user(self,event_id:int, user_id:int):
        db_event_user = self.get_event_user(event_id, user_id)
        self.db.delete(db_event_user)
        self.db.commit()
        return db_event_user
