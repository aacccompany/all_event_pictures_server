from pydantic import BaseModel, computed_field
from schemas.auth import UserResponse
from typing import Optional


class Image(BaseModel):
    public_id: str
    secure_url: str


class ImageUpload(Image):
    optimized_url: str | None = None
    original_url: str | None = None
    face_embeddings: list[list[float]] | None = None
    face_boxes: list[list[float]] | None = None
    status: str = "PENDING_AI"


class ImageIdList(BaseModel):
    image_ids: list[int]


class ImageResponse(Image):
    id: int
    optimized_url: str | None = None
    original_url: str | None = None
    face_embeddings: list[list[float]] | None = None
    face_boxes: list[list[float]] | None = None
    status: str
    created_by: UserResponse

    @computed_field
    @property
    def preview_url(self) -> str:
        """
        Return the optimized (watermarked WebP) URL for web display.
        Falls back to secure_url for old Cloudinary-backed images.
        """
        return self.optimized_url or self.secure_url


class ImageManageGlobalResponse(ImageResponse):
    event_id: int
    event_name: str


# Import at the end to avoid circular dependency
from schemas.event import EventBasic

class ImageResponseWithEvent(ImageResponse):
    """Image response with event relationship for cart/display purposes"""
    event: Optional[EventBasic] = None
