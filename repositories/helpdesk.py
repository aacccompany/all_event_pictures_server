from sqlalchemy.orm import Session
from models.helpdesk import HelpdeskDB
from schemas.helpdesk import HelpdeskCreate, HelpdeskUpdateStatus

class HelpdeskRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self):
        return self.db.query(HelpdeskDB).order_by(HelpdeskDB.created_at.desc()).all()

    def get_by_user(self, user_id: int):
        return self.db.query(HelpdeskDB).filter(HelpdeskDB.user_id == user_id).order_by(HelpdeskDB.created_at.desc()).all()

    def get_by_id(self, ticket_id: int):
        return self.db.query(HelpdeskDB).filter(HelpdeskDB.id == ticket_id).first()

    def create(self, user_id: int, helpdesk: HelpdeskCreate):
        db_hd = HelpdeskDB(**helpdesk.model_dump(), user_id=user_id)
        self.db.add(db_hd)
        self.db.commit()
        self.db.refresh(db_hd)
        return db_hd

    def update_status(self, ticket_id: int, status_update: HelpdeskUpdateStatus):
        db_hd = self.get_by_id(ticket_id)
        if db_hd:
            db_hd.status = status_update.status
            self.db.commit()
            self.db.refresh(db_hd)
        return db_hd
