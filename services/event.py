from sqlalchemy.orm import Session
from repositories.event import EventRepository
from schemas.event import EventCreate, EventUpdate
from schemas.auth import UserResponse
from fastapi import HTTPException, status


class EventService:
    def __init__(self, db = Session):
        self.repo = EventRepository(db)
        
    def create_event(self, event:EventCreate, user:UserResponse):
        return self.repo.create(event, user)
        
    def get_events(self):
        events = self.repo.get_all()
        if not events:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Events not found")
        return events
    
    def get_event(self, event_id:int):
        event = self.repo.get_by_id(event_id)
        if not event:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Event ID {event_id} not found")
        return event
    
    def update_event(self, event_id:int, event:EventUpdate, user:UserResponse):
        if not self.repo.get_by_id(event_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Event ID {event_id} not found")
        return self.repo.update(event_id, event, user)
    
    def remove_event(self, event_id:int):
        if not self.repo.get_by_id(event_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Event ID {event_id} not found")
        self.repo.remove(event_id)
        return {"message": f"Event ID {event_id} deleted"}
    
    def search_events(self, title:str):
        events = self.repo.search_by_title(title)
        if not events:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Events not found")
        return events
    
    def get_active_events(self):
        events = self.repo.get_active()
        if not events:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Events not found")
        return events