from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class HelpdeskBase(BaseModel):
    topic: str
    message: str

class HelpdeskCreate(HelpdeskBase):
    pass

class HelpdeskResponse(HelpdeskBase):
    id: int
    user_id: int
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class HelpdeskUpdateStatus(BaseModel):
    status: str
