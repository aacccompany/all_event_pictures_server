from sqlalchemy.orm import Session
from models.cart_image import CartImageDB


class CartImageRepository:
    def __init__(self, db=Session):
        self.db = db
        
    def get_by_id(self, cart_id: int, image_id: int):
        return self.db.query(CartImageDB).filter(CartImageDB.cart_id == cart_id, CartImageDB.image_id == image_id).first()

    def add_images_to_cart(self, cart_id: int, images_id: list[int]):
        cart_image = CartImageDB(cart_id=cart_id, image_id=images_id)
        self.db.add(cart_image)
        self.db.commit()
        self.db.refresh(cart_image)
        return cart_image
    
    def remove_image_from_cart(self, cart_image_id:int):
        cart_image = self.db.query(CartImageDB).filter(CartImageDB.id == cart_image_id).first()
        if cart_image:
            self.db.delete(cart_image)
            self.db.commit()
        return cart_image
    
    

        
