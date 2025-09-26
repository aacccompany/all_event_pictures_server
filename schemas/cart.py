from pydantic import BaseModel
from datetime import datetime
from schemas.image import ImageResponse
from schemas.auth import UserResponse

class CartImageResponse(BaseModel):
    id: int
    image: ImageResponse  

    class Config:
        from_attributes = True

class CartResponse(BaseModel):
    id: int
    paymentStatus: bool
    downloaded: bool
    event_name: str | None = None # เพิ่มสำหรับ Download History
    number_of_files: int | None = None # เพิ่มสำหรับ Download History
    purchase_date: datetime | None = None # เพิ่มสำหรับ Download History
    cart_images: list[CartImageResponse] 
    created_by: UserResponse

    class Config:
        from_attributes = True

class AddImagesToCart(BaseModel):
    images_id: list[int]
