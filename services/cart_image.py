from sqlalchemy.orm import Session
from repositories.cart import CartRepository
from repositories.image import ImageRepository
from repositories.cart_image import CartImageRepository
from fastapi import HTTPException, status

class CartImageService:
    def __init__(self, db = Session):
        self.repo = CartImageRepository(db)
        self.cart = CartRepository(db)
        self.image = ImageRepository(db)
        
    def add_images_to_cart(self, user_id:int, images_id:list[int]):
        cart = self.cart.get_by_payment(user_id)
        if not cart:
            cart = self.cart.create(user_id)

        images = self.image.get_all(images_id)
        if not images:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Images not found")

        for img_id in images_id:
            if self.repo.get_by_id(cart.id, img_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"already image ID: {img_id}"
                )
            self.repo.add_images_to_cart(cart.id, img_id)

        return cart