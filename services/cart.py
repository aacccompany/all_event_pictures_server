from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from repositories.cart import CartRepository

class CartService:
    def __init__(self, db: Session):
        self.cart_repo = CartRepository(db)

    def get_my_cart(self, user_id: int):
        cart = self.cart_repo.get_my_cart(user_id)
        if not cart:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cart not found"
            )
        return cart
