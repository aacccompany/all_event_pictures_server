from sqlalchemy.orm import Session
from repositories.helpdesk import HelpdeskRepository
from schemas.helpdesk import HelpdeskCreate, HelpdeskUpdateStatus
from fastapi import HTTPException

def create_ticket(db: Session, user_id: int, ticket: HelpdeskCreate):
    repo = HelpdeskRepository(db)
    created_ticket = repo.create(user_id=user_id, helpdesk=ticket)
    
    from models.user import UserDB
    from services.notification_service import NotificationService
    notif_service = NotificationService(db)
    
    super_admins = db.query(UserDB).filter(UserDB.role == "super-admin").all()
    for admin in super_admins:
        notif_service.create_notification(
            user_id=admin.id,
            title="New Helpdesk Ticket",
            message=f"Ticket '{ticket.topic}' has been submitted."
        )
        
    return created_ticket

def get_my_tickets(db: Session, user_id: int):
    repo = HelpdeskRepository(db)
    return repo.get_by_user(user_id)

def get_all_tickets(db: Session):
    repo = HelpdeskRepository(db)
    return repo.get_all()

def update_ticket_status(db: Session, ticket_id: int, status_update: HelpdeskUpdateStatus):
    repo = HelpdeskRepository(db)
    ticket = repo.get_by_id(ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return repo.update_status(ticket_id, status_update)
