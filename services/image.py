from sqlalchemy.orm import Session
from repositories.image import ImageRepository
from schemas.image import ImageUpload, ImageResponse
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
            db_image = self.repo.upload(event_id, user, data)
            image_response = ImageResponse(
                id=db_image.id,
                public_id=db_image.public_id,
                secure_url=db_image.secure_url,
                created_by=db_image.created_by
            )

            result.append(image_response)
        return result
