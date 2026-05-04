from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from schemas.image import ImageResponseWithEvent
from schemas.auth import UserResponse

class CartImageResponse(BaseModel):
    id: int
    image: ImageResponseWithEvent

    class Config:
        from_attributes = True

class CartResponse(BaseModel):
    id: int
    paymentStatus: bool
    downloaded: bool
    event_name: Optional[str] = None # เพิ่มสำหรับ Download History
    number_of_files: Optional[int] = None # เพิ่มสำหรับ Download History
    purchase_date: Optional[datetime] = None # เพิ่มสำหรับ Download History
    cart_images: List[CartImageResponse]
    created_by: UserResponse

    class Config:
        from_attributes = True

class AddImagesToCart(BaseModel):
    images_id: List[int]
