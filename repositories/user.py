from sqlalchemy.orm import Session
from models.user import UserDB
from schemas.user import UserCreate

class UserRepository:
    def __init__(self, db:Session):
        self.db = db
    
    def get_by_email(self, user_email:str):
        return self.db.query(UserDB).filter(UserDB.email == user_email).first()
    
    def create(self, user:UserCreate):
        db_user = UserDB(**user.model_dump())
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user
    
    
        