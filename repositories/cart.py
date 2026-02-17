from sqlalchemy.orm import Session
from models.cart import CartDB
from models.cart_image import CartImageDB
from models.image import ImageDB
from models.event import EventDB
from fastapi import HTTPException, status


class CartRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, user_id: int):
        cart = CartDB(created_by_id=user_id, updated_by_id=user_id)
        self.db.add(cart)
        self.db.commit()
        self.db.refresh(cart)
        return cart
        
    def get_my_cart(self, user_id:int):
        return self.db.query(CartDB).filter(CartDB.created_by_id == user_id, CartDB.paymentStatus == False, CartDB.downloaded == False).first()
    
    def my_images(self, user_id:int):
        return self.db.query(CartDB).filter(CartDB.created_by_id == user_id, CartDB.downloaded == True).all()
    
    def get_cart_by_id(self, user_id: int, cart_id: int):
        return self.db.query(CartDB).filter(CartDB.id == cart_id, CartDB.created_by_id == user_id).first()

    def recent_downloaded_carts(self, limit: int = 10):
        return (
            self.db.query(CartDB)
            .filter(CartDB.downloaded == True)
            .order_by(CartDB.created_at.desc())
            .limit(limit)
            .all()
        )

    def get_recent_sales_by_identity(self, user_id: int, limit: int = 10):
        return (
            self.db.query(CartDB)
            .join(CartImageDB, CartDB.id == CartImageDB.cart_id)
            .join(ImageDB, CartImageDB.image_id == ImageDB.id)
            .join(EventDB, ImageDB.event_id == EventDB.id)
            .filter(
                CartDB.downloaded == True,
                ImageDB.created_by_id == user_id
            )
            .order_by(CartDB.created_at.desc())
            .limit(limit)
            .all()
        )

    def get_recent_sales_by_event_creator(self, user_id: int, limit: int = 10):
        return (
            self.db.query(CartDB)
            .join(CartImageDB, CartDB.id == CartImageDB.cart_id)
            .join(ImageDB, CartImageDB.image_id == ImageDB.id)
            .join(EventDB, ImageDB.event_id == EventDB.id)
            .filter(
                CartDB.downloaded == True,
                EventDB.created_by_id == user_id
            )
            .order_by(CartDB.created_at.desc())
            .limit(limit)
            .all()
        )
