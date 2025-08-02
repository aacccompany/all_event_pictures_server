from sqlalchemy.orm import Session
from repositories.image import ImageRepository
from repositories.event import EventRepository
from schemas.image import ImageUpload
from schemas.auth import UserResponse
from services.cloudinary import CloudinaryService
from fastapi import UploadFile


class ImageService:
    def __init__(self, db = Session):
        self.repo = ImageRepository(db)
        self.repo_event = EventRepository(db)
        
    async def upload_images(self, images: list[UploadFile], event_id:int, user: UserResponse):
        upload_images = await CloudinaryService.upload_images(images, user)
        result = []
        for i in upload_images:
            data = ImageUpload(
                public_id=i["public_id"],
                secure_url=i["secure_url"],
                event_id=event_id
            )
            result.append(self.repo.upload(data, user))
        return result
        