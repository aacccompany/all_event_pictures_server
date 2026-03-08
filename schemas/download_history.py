from pydantic import BaseModel
from datetime import datetime

class DownloadHistoryImageResponse(BaseModel):
    id: int
    secure_url: str
    public_id: str

    class Config:
        from_attributes = True

class DownloadHistoryResponse(BaseModel):
    id: int
    event_name: str
    number_of_files: int
    purchase_date: datetime
    expiration_date: datetime | None = None
    images: list[DownloadHistoryImageResponse] = []
    
    class Config:
        from_attributes = True


class RecentSaleResponse(BaseModel):
    sale_id: int
    event_name: str
    photo_count: int
    purchased_at: datetime
    buyer_name: str | None = None
    buyer_email: str | None = None
    image_url: str | None = None
    total_amount: float | None = 0.0
    earnings: float | None = 0.0
    role_split: str | None = None

    class Config:
        from_attributes = True

