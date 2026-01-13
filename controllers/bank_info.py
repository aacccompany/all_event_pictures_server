from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from core.database import get_db
from models.user import UserDB
from middleware.auth import get_current_user
from services.bank_info import BankInfoService
from schemas.bank_info import BankInfoResponse, BankInfoCreate
from typing import Annotated

router = APIRouter()

@router.get("/bank-info", response_model=BankInfoResponse | None)
async def get_bank_info(
    user: Annotated[UserDB, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    return BankInfoService(db).get_bank_info(user.id)

@router.put("/bank-info", response_model=BankInfoResponse)
async def update_bank_info(
    bank_info: BankInfoCreate,
    user: Annotated[UserDB, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    return BankInfoService(db).create_or_update_bank_info(user.id, bank_info)
