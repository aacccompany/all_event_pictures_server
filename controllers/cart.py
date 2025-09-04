from fastapi import APIRouter, Depends
from schemas.cart import CartResponse
from schemas.auth import UserResponse
from middleware.auth import get_current_user
from services.cart import CartService
from sqlalchemy.orm import Session
from core.database import get_db

router = APIRouter()

@router.get("/my-cart", response_model=CartResponse)
def get(user: UserResponse = Depends(get_current_user), db: Session = Depends(get_db)):
    return CartService(db).get_my_cart(user.id)