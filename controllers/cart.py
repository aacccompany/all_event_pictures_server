from fastapi import APIRouter, Depends, HTTPException
from schemas.cart import CartResponse
from schemas.auth import UserResponse
from schemas.auth import UserResponse
from middleware.auth import get_current_user_public, get_current_active_user, get_current_admin
from services.cart import CartService
from services.stripe_service import create_checkout_session
from sqlalchemy.orm import Session
from core.database import get_db
from fastapi.responses import StreamingResponse
from schemas.download_history import DownloadHistoryResponse, RecentSaleResponse

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
    
@router.get("/download-cart/{cart_id}") # Endpoint ใหม่สำหรับ Re-download
def re_download_cart(
    cart_id: int,
    user: UserResponse = Depends(get_current_user_public),
    db: Session = Depends(get_db)
):
    zip_buffer, downloaded_cart_id = CartService(db).download_cart_zip_by_id(user.id, cart_id)
    
    return StreamingResponse(
        zip_buffer,
        media_type="application/x-zip-compressed",
        headers={"Content-Disposition": f"attachment; filename=cart_{downloaded_cart_id}.zip"}
    )
    
@router.post("/my-cart/create-checkout-session")
def create_stripe_checkout_session(
    success_url: str,
    cancel_url: str,
    user: UserResponse = Depends(get_current_user_public),
    db: Session = Depends(get_db)
):
    cart_service = CartService(db)
    cart = cart_service.get_my_cart(user.id)
    if not cart or not cart.cart_images:
        raise HTTPException(status_code=404, detail="Cart is empty or not found")
    
    checkout_session_url = create_checkout_session(cart.cart_images, success_url, cancel_url)
    return {"checkout_url": checkout_session_url}

@router.get("/my-images", response_model=CartResponse)
def get_my_images(user: UserResponse = Depends(get_current_user_public), db: Session = Depends(get_db)):
    return CartService(db).get_my_images(user.id)

@router.get("/my-download-history", response_model=list[DownloadHistoryResponse])
def get_download_history_endpoint(
    user: UserResponse = Depends(get_current_user_public),
    db: Session = Depends(get_db)
):
    return CartService(db).get_download_history(user.id)

@router.get("/recent-sales", response_model=list[RecentSaleResponse])
def get_recent_sales(limit: int = 5, db: Session = Depends(get_db)):
    return CartService(db).get_recent_sales(limit)

@router.get("/recent-sales/my-sales", response_model=list[RecentSaleResponse])
def get_recent_sales_by_user(
    limit: int = 5, 
    user: UserResponse = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    return CartService(db).get_recent_sales_by_user(user.id, limit)

@router.get("/recent-sales/from-my-events", response_model=list[RecentSaleResponse])
def get_recent_sales_from_my_events(
    limit: int = 5,
    user: UserResponse = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    return CartService(db).get_recent_sales_from_my_events(user.id, limit)
