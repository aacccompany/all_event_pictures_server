from pydantic import BaseModel, computed_field
from schemas.auth import UserResponse
from services.cloudinary import CloudinaryService


class Image(BaseModel):
    public_id:str
    secure_url:str


class ImageUpload(Image):
    face_embeddings: list[list[float]] | None = None
    face_boxes: list[list[float]] | None = None


class ImageResponse(Image):
    id: int
    face_embeddings: list[list[float]] | None = None
    face_boxes: list[list[float]] | None = None
    created_by: UserResponse
    
    @computed_field 
    @property
    def preview_url(self) -> str:
        return CloudinaryService.get_watermarked_url(self.public_id)
    
    class Config:
        from_attributes = True
