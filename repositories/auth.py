from sqlalchemy.orm import Session
from models.user import UserDB
from models.event import EventDB
from schemas.auth import UserCreate
from models.event_user import EventUserDB


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, user_email: str):
        return self.db.query(UserDB).filter(UserDB.email == user_email).first()

    def create(self, user: UserCreate):
        db_user = UserDB(**user.model_dump())
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def get_by_events(self, user_id: int):
        return (
            self.db.query(EventDB)
            .filter(EventDB.deleted_at.is_(None), EventDB.created_by_id == user_id)
            .order_by(EventDB.date.asc())
            .all()
        )
    
    def get_by_events_joined(self, user_id:int):
        return (
            self.db.query(EventDB)  
            .join(EventUserDB, EventUserDB.event_id == EventDB.id)
            .filter(EventUserDB.user_id == user_id, EventDB.deleted_at.is_(None))
            .all()
        )
        
    def search_by_email(self, email:str):
        return self.db.query(UserDB).filter(UserDB.email.ilike(f"%{email}%")).all()

    def update(self, user: UserDB, update_data: dict):
        for key, value in update_data.items():
            setattr(user, key, value)
        self.db.commit()
        self.db.refresh(user)
        return user
