from sqlalchemy.orm import Session
from repositories.item import ItemRepository
from schemas.item import ItemCreate
from fastapi import HTTPException

class ItemService:
    def __init__(self, db = Session):
        self.repo = ItemRepository(db)
        
    def create_item(self, item:ItemCreate):
        return self.repo.create(item)
    
    def get_items(self):
        return self.repo.get_all()
    
    def get_item(self, item_id:int):
        item = self.repo.get_by_id(item_id)
        if not item: 
            raise HTTPException(status_code=404, detail=f"title ID {item_id} not found")
        return item
    
    def update_item(self, item_id:int, item:ItemCreate):
        if not self.repo.get_by_id(item_id):
            raise HTTPException(status_code=404, detail=f"title ID {item_id} not found")
        return self.repo.update(item_id, item)
    
    def remove_item(self, item_id:int):
        if not self.repo.get_by_id(item_id):
            raise HTTPException(status_code=404, detail=f"title ID {item_id} not found")
        self.repo.remove(item_id)
        return {'message': f"Item ID {item_id} deleted"}