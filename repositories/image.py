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

    def update_face_embeddings(self, image_id: int, face_embeddings: list[list[float]], face_boxes: list[list[float]]):
        db_image = self.db.query(ImageDB).filter(ImageDB.id == image_id).first()
        if db_image:
            db_image.face_embeddings = face_embeddings
            db_image.face_boxes = face_boxes
            db_image.status = "COMPLETED"
            self.db.commit()
            self.db.refresh(db_image)
        return db_image

    def get_images_by_event_and_role(self, event_id: int, user: UserResponse):
        query = self.db.query(ImageDB).filter(ImageDB.event_id == event_id)
        if user.role == "super-admin":
            return query.all()
        # the admin check will be done in the service layer where it checks EventDB creator.
        # But wait, if user is photographer, they only see their own uploads
        if user.role == "user" or user.role == "user-public":
            query = query.filter(ImageDB.created_by_id == user.id)
        return query.all()

    def get_all_images_by_role(self, user: UserResponse):
        from sqlalchemy.orm import joinedload
        from models.event import EventDB
        
        query = self.db.query(ImageDB).options(joinedload(ImageDB.event))
        
        if user.role == "super-admin":
            return query.order_by(ImageDB.created_at.desc()).all()
        elif user.role == "admin":
            query = query.join(EventDB).filter(EventDB.created_by_id == user.id)
            return query.order_by(ImageDB.created_at.desc()).all()
        elif user.role in ["user", "user-public"]:
            query = query.filter(ImageDB.created_by_id == user.id)
            return query.order_by(ImageDB.created_at.desc()).all()
            
        return []

    def get_images_by_ids(self, image_ids: list[int]):
        return self.db.query(ImageDB).filter(ImageDB.id.in_(image_ids)).all()

    def delete_images(self, image_ids: list[int]):
        self.db.query(ImageDB).filter(ImageDB.id.in_(image_ids)).delete(synchronize_session=False)
        self.db.commit()
