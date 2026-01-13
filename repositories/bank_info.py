from sqlalchemy.orm import Session
from models.bank_info import BankInfoDB
from schemas.bank_info import BankInfoCreate, BankInfoUpdate

class BankInfoRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_user_id(self, user_id: int):
        return self.db.query(BankInfoDB).filter(BankInfoDB.user_id == user_id).first()

    def create(self, user_id: int, bank_info: BankInfoCreate):
        db_bank_info = BankInfoDB(**bank_info.model_dump(), user_id=user_id)
        self.db.add(db_bank_info)
        self.db.commit()
        self.db.refresh(db_bank_info)
        return db_bank_info

    def update(self, db_bank_info: BankInfoDB, bank_info: BankInfoUpdate):
        update_data = bank_info.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_bank_info, key, value)
        self.db.commit()
        self.db.refresh(db_bank_info)
        return db_bank_info
