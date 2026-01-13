from sqlalchemy.orm import Session
from repositories.bank_info import BankInfoRepository
from schemas.bank_info import BankInfoCreate, BankInfoUpdate

class BankInfoService:
    def __init__(self, db: Session):
        self.repo = BankInfoRepository(db)

    def get_bank_info(self, user_id: int):
        return self.repo.get_by_user_id(user_id)

    def create_or_update_bank_info(self, user_id: int, bank_info: BankInfoCreate):
        existing_info = self.repo.get_by_user_id(user_id)
        if existing_info:
            return self.repo.update(existing_info, bank_info)
        return self.repo.create(user_id, bank_info)
