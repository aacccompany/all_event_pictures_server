from pydantic import BaseModel
from datetime import datetime

class DownloadHistoryResponse(BaseModel):
    id: int
    event_name: str
    number_of_files: int
    purchase_date: datetime
    
    class Config:
        from_attributes = True


class RecentSaleResponse(BaseModel):
    event_name: str
    photo_count: int
    purchased_at: datetime
    image_url: str | None = None


