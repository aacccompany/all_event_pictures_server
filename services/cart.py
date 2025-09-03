from sqlalchemy.orm import Session
from repositories.cart import CartRepository
from repositories.image import ImageRepository
from fastapi import HTTPException, status
import uuid

class CartService:
    def __init__(self, db = Session):
        self.repo = CartRepository(db)
        self.image = ImageRepository(db)
        
    def add_images_to_cart(self, user_id:int, images_id:list[int]):
        cart = self.repo.get_by_payment(user_id)
        if not cart:
            cart = self.repo.create(user_id)
        
        images = self.image.get_all(images_id)
        if not images:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Images not found")
        
        self.image.add_cart(images, cart.id, user_id)
        return cart