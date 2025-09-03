from pydantic import BaseModel
from datetime import datetime
from schemas.image import ImageResponse

class CartResponse(BaseModel):
    id: int
    paymentStatus: bool
    created_at: datetime
    updated_at: datetime
    images_by_user: list[ImageResponse]

    class Config:
        from_attributes = True

class AddImagesToCart(BaseModel):
    images_id: list[int]