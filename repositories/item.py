from sqlalchemy.orm import Session
from models.item import ItemDB
from schemas.item import ItemCreate


class ItemRepository:
    def __init__(self, db=Session):
        self.db = db

    def get_all(self):
        return self.db.query(ItemDB).all()

    def get_by_id(self, item_id: int):
        return self.db.query(ItemDB).filter(ItemDB.id == item_id).first()

    def create(self, item: ItemCreate):
        db_item = ItemDB(**item.model_dump())
        self.db.add(db_item)
        self.db.commit()
        self.db.refresh(db_item)
        return db_item

    def update(self, item_id: int, item: ItemCreate):
        db_item = self.get_by_id(item_id)
        if db_item:
            for key, value in item.model_dump().items():
                setattr(db_item,key, value)
            self.db.commit()
            self.db.refresh(db_item)
            return db_item

    def remove(self, item_id: int):
        db_item = self.get_by_id(item_id)
        if db_item:
            self.db.delete(db_item)
            self.db.commit()
        return db_item
