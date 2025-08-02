from pydantic import BaseModel
from schemas.auth import UserResponse


class Image(BaseModel):
    public_id:str
    secure_url:str
    event_id:int


class ImageUpload(Image):
    pass


class ImageResponse(Image):
    id: int
    created_by: UserResponse
    
    class Config:
        from_attributes = True
