from pydantic import BaseModel
from decimal import Decimal

class Item(BaseModel):
    title: str
    description: str | None = None
    price: Decimal
    
class ItemCreate(Item):
    pass

class ItemResponse(Item):
    id: int
    
    class Config:
        orm_mode = True