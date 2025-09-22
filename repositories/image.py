from sqlalchemy.orm import Session
from schemas.image import ImageUpload
from schemas.auth import UserResponse
from models.image import ImageDB


class ImageRepository():
    def __init__(self, db = Session):
        self.db = db
        
    def upload(self, event_id:int, user:UserResponse, images:ImageUpload):
        db_image = ImageDB(**images.model_dump(), created_by_id=user.id, updated_by_id=user.id, event_id=event_id)
        self.db.add(db_image)
        self.db.commit()
        self.db.refresh(db_image)
        return db_image
    
    def get_all(self, images_id:list[int]):
        return self.db.query(ImageDB).filter(ImageDB.id.in_(images_id)).all()

    def get_images_with_faces_by_event_id(self, event_id: int):
        return self.db.query(ImageDB).filter(ImageDB.event_id == event_id, ImageDB.face_embeddings != None).all()
    