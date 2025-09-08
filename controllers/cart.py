from fastapi import APIRouter, Depends
from schemas.cart import CartResponse
from schemas.auth import UserResponse
from middleware.auth import get_current_user_public
from services.cart import CartService
from sqlalchemy.orm import Session
from core.database import get_db
from fastapi.responses import StreamingResponse

router = APIRouter()

@router.get("/my-cart", response_model=CartResponse)
def get(user: UserResponse = Depends(get_current_user_public), db: Session = Depends(get_db)):
    return CartService(db).get_my_cart(user.id)

@router.get("/my-cart/download")
def download_my_cart(
    user: UserResponse = Depends(get_current_user_public),
    db: Session = Depends(get_db)
):
    zip_buffer, cart_id = CartService(db).download_cart_zip(user.id)

    return StreamingResponse(
        zip_buffer,
        media_type="application/x-zip-compressed",
        headers={"Content-Disposition": f"attachment; filename=cart_{cart_id}.zip"}
    )
    
@router.get("/my-images", response_model=CartResponse)
def get(user: UserResponse = Depends(get_current_user_public), db: Session = Depends(get_db)):
    return CartService(db).get_my_images(user.id)