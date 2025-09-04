from fastapi import APIRouter, Depends
from schemas.cart import CartResponse, AddImagesToCart
from schemas.auth import UserResponse
from middleware.auth import get_current_user
from services.cart_image import CartImageService
from sqlalchemy.orm import Session
from core.database import get_db

router = APIRouter()

@router.post("/cart", response_model=CartResponse)
def add_images_to_cart(images:AddImagesToCart, user: UserResponse = Depends(get_current_user), db: Session = Depends(get_db)):
    return CartImageService(db).add_images_to_cart(user.id, images.images_id)