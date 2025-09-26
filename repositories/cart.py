from sqlalchemy.orm import Session
from models.cart import CartDB
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