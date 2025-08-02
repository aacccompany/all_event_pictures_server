from sqlalchemy.orm import Session
from schemas.image import ImageUpload
from schemas.auth import UserResponse
from models.image import ImageDB


class ImageRepository():
    def __init__(self, db = Session):
        self.db = db
        
    def upload(self, images:ImageUpload, user:UserResponse):
        db_image = ImageDB(**images.model_dump(), created_by_id=user.id, updated_by_id=user.id)
        self.db.add(db_image)
        self.db.commit()
        self.db.refresh(db_image)
        return db_image
    