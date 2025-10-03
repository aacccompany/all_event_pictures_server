from sqlalchemy.orm import Session
from repositories.event_user import EventUserRepository
from repositories.event import EventRepository
from repositories.auth import UserRepository
from fastapi import HTTPException, status
from schemas.event_user import EventUserJoin


class EventUserService:
    def __init__(self, db =Session):
        self.repo = EventUserRepository(db)
        self.event_repo = EventRepository(db)
        self.user_repo = UserRepository(db)
        
    def join_event(self, event_id:int, user_id:int):
       event = self.event_repo.get_by_id(event_id)
       if not event:
           raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Event not found")
       
       if event.active != True:
           raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Event not active")
       
       if event.event_type == "Private":
           raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Private event, invite only")
       
       if event.limit and event.joined_count >= event.limit:
           raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Event is full")
       
       if self.repo.get_event_user(event.id, user_id):
           raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Already joined")
       
       db_event_user = self.repo.add_user(event_id, user_id)
       event.joined_count += 1  
       return db_event_user
       
    def invite_events(self, event_id: int, user: EventUserJoin):
        event = self.event_repo.get_by_id(event_id)
        if not event:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Event not found")

        if event.event_type != "Private":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only private events")

        invited_users = []
        for i in user.user_emails:
            user = self.user_repo.get_by_email(i)
            if not user:
                raise HTTPException( status_code=status.HTTP_404_NOT_FOUND, detail=f"User with email {i} not found")   
            if self.repo.get_event_user(event_id, user.id):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{i} Already joined")

            # Check if the invited user has the 'user' role
            if user.role != "user":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"User with email {i} does not have the \"photographer\" role and cannot be invited."
                )

            event_user = self.repo.add_user(event_id, user.id)
            invited_users.append(event_user)

        event.joined_count += len(invited_users)
        return invited_users

    
    def leave_event(self, event_id:int, user_id:int):
        event = self.event_repo.get_by_id(event_id)
        if not event:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Event not found")
        
        event_user = self.repo.get_event_user(event_id ,user_id)
        if not event_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User has not joined this event")
        
        self.repo.remove_event_user(event_id, user_id)
        if event.joined_count > 0:
            event.joined_count -= 1
        return {"message": "Leave event"}
