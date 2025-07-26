from sqlalchemy.orm import Session
from repositories.event import EventRepository
from schemas.event import EventCreate
from schemas.auth import UserResponse

class EventService:
    def __init__(self, db = Session):
        self.repo = EventRepository(db)
        
    def create_event(self, event:EventCreate, user:UserResponse):
        return self.repo.create(event, user)
        