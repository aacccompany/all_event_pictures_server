from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from models.transaction import TransactionStatus
from models.wallet import WalletTransactionType, WithdrawalStatus

class WalletTransactionResponse(BaseModel):
    id: int
    user_id: int
    amount: int
    type: WalletTransactionType
    description: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class WithdrawalRequestCreate(BaseModel):
    amount: int

class WithdrawalRequestResponse(BaseModel):
    id: int
    user_id: int
    amount: int
    status: WithdrawalStatus
    bank_snapshot: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class VerifyPaymentRequest(BaseModel):
    session_id: str
    # cart_id might be needed if not implicit in user context
