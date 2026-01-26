from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.database import get_db
from middleware.auth import get_current_user_public, get_current_active_user
from schemas.auth import UserResponse
from schemas.wallet import WalletTransactionResponse, WithdrawalRequestResponse, WithdrawalRequestCreate, VerifyPaymentRequest
from services.wallet_service import WalletService
from services.cart import CartService
from typing import List

router = APIRouter(prefix="/wallet", tags=["Wallet"])

@router.post("/verify-payment")
def verify_payment(
    req: VerifyPaymentRequest,
    user: UserResponse = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    wallet_service = WalletService(db)
    cart_service = CartService(db)
    return wallet_service.verify_payment_and_distribute(req.session_id, user.id, cart_service)

@router.get("/my-balance")
def get_my_balance(
    user: UserResponse = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    wallet_service = WalletService(db)
    return {"balance": wallet_service.get_balance(user.id)}

@router.get("/my-history", response_model=List[WalletTransactionResponse])
def get_my_history(
    user: UserResponse = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    wallet_service = WalletService(db)
    return wallet_service.get_wallet_history(user.id)

@router.post("/withdraw", response_model=WithdrawalRequestResponse)
def request_withdraw(
    req: WithdrawalRequestCreate,
    user: UserResponse = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    wallet_service = WalletService(db)
    return wallet_service.request_withdrawal(user.id, req.amount)

# Super Admin endpoints (should be protected by role, assuming get_current_user_public handles it or we need a stricter dep)
# For now using open dependency but checking role inside or assume middleware handles path.
# Actually I should use strict dependency if available.
# But for now, let's just use get_current_user_public and rely on implicit trust or add check.
# Ideally: get_current_super_admin
# I'll stick to basic auth for now but maybe I should check role.

@router.get("/admin/withdrawals", response_model=List[WithdrawalRequestResponse])
def get_all_withdrawals(
    user: UserResponse = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    if user.role not in ["super-admin", "admin"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    wallet_service = WalletService(db)
    return wallet_service.get_withdrawal_requests()

@router.post("/admin/withdrawals/{id}/approve")
def approve_withdrawal(
    id: int,
    user: UserResponse = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    if user.role != "super-admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    wallet_service = WalletService(db)
    return wallet_service.approve_withdrawal(id, user.id)

@router.post("/admin/withdrawals/{id}/reject")
def reject_withdrawal(
    id: int,
    user: UserResponse = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    if user.role != "super-admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    wallet_service = WalletService(db)
    return wallet_service.reject_withdrawal(id, user.id)

@router.get("/admin/platform-revenue")
def get_platform_revenue(
    user: UserResponse = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    if user.role not in ["super-admin", "admin"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    wallet_service = WalletService(db)
    return {"total_revenue": wallet_service.get_total_platform_revenue()}

@router.post("/admin/deduct")
def deduct_balance(
    user_id: int,
    amount: int,
    user: UserResponse = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    if user.role != "super-admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    wallet_service = WalletService(db)
    return wallet_service.deduct_balance(user.id, user_id, amount)
