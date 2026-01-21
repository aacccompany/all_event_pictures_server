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

    def create(self, user: UserCreate | dict):
        if isinstance(user, dict):
            db_user = UserDB(**user)
        else:
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

    def get_all(self, skip: int = 0, limit: int = 100, include_deleted: bool = False, role: str = None):
        query = self.db.query(UserDB)
        if not include_deleted:
            query = query.filter(UserDB.deleted_at.is_(None))
        
        if role:
            query = query.filter(UserDB.role == role)
        
        total = query.count()
        items = query.offset(skip).limit(limit).all()
        return items, total

    def get_by_id(self, user_id: int):
        return self.db.query(UserDB).filter(UserDB.id == user_id, UserDB.deleted_at.is_(None)).first()
    
    def delete(self, user_id: int):
        from datetime import datetime, timezone
        user = self.get_by_id(user_id)
        if user:
            user.deleted_at = datetime.now(timezone.utc)
            user.enabled = False
            self.db.commit()
            self.db.refresh(user)
        return user
