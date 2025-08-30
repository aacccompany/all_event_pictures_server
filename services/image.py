from sqlalchemy.orm import Session
from repositories.image import ImageRepository
from schemas.image import ImageUpload
from schemas.auth import UserResponse
from services.cloudinary import CloudinaryService
from fastapi import UploadFile
from services.event import EventService

class ImageService:
    def __init__(self, db = Session):
        self.repo = ImageRepository(db)
        self.event_service = EventService(db)
        
    async def upload_images(self, images: list[UploadFile], event_id:int, user: UserResponse):
        self.event_service.get_event(event_id)
        upload_images = await CloudinaryService.upload_images(images, user)
        result = []
        for i in upload_images:
            data = ImageUpload(
                public_id=i["public_id"],
                secure_url=i["secure_url"],
            )
            result.append(self.repo.upload(event_id, user,data))
        return result
        