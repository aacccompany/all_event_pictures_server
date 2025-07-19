from fastapi import APIRouter, Depends
from schemas.item import ItemResponse, ItemCreate
from sqlalchemy.orm import Session
from core.database import get_db
from services.item import ItemService
from typing import List
from middleware.auth import get_current_admin

router = APIRouter()

@router.post("/item", response_model=ItemResponse)
async def create_item(item:ItemCreate, db:Session = Depends(get_db)):
    return ItemService(db).create_item(item)

@router.get("/items", response_model=List[ItemResponse])
async def get_items(db:Session = Depends(get_db)):
    return ItemService(db).get_items()

@router.get("/item/{item_id}", response_model=ItemResponse)
async def get_item(item_id:int, db:Session = Depends(get_db)):
    return ItemService(db).get_item(item_id)

@router.patch("/item/{item_id}")
async def update_item(item_id: int, item: ItemCreate, db: Session = Depends(get_db), user = Depends(get_current_admin)):
    return ItemService(db).update_item(item_id, item)

@router.delete("/item/{item_id}")
async def remove_item(item_id:int, db:Session = Depends(get_db)):
    return ItemService(db).remove_item(item_id)