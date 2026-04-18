from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.database import get_db
from schemas.helpdesk import HelpdeskCreate, HelpdeskResponse, HelpdeskUpdateStatus
from services.helpdesk import create_ticket, get_my_tickets, get_all_tickets, update_ticket_status
from middleware.auth import get_current_active_user, get_current_super_admin
from typing import List

router = APIRouter(prefix="/helpdesk", tags=["Helpdesk"])

@router.post("/", response_model=HelpdeskResponse)
def api_create_ticket(ticket: HelpdeskCreate, db: Session = Depends(get_db), current_user=Depends(get_current_active_user)):
    return create_ticket(db, current_user.id, ticket)

@router.get("/my", response_model=List[HelpdeskResponse])
def api_get_my_tickets(db: Session = Depends(get_db), current_user=Depends(get_current_active_user)):
    return get_my_tickets(db, current_user.id)

@router.get("/", response_model=List[HelpdeskResponse])
def api_get_all_tickets(db: Session = Depends(get_db), current_user=Depends(get_current_super_admin)):
    return get_all_tickets(db)

@router.patch("/{ticket_id}", response_model=HelpdeskResponse)
def api_update_ticket_status(ticket_id: int, status_update: HelpdeskUpdateStatus, db: Session = Depends(get_db), current_user=Depends(get_current_super_admin)):
    return update_ticket_status(db, ticket_id, status_update)
