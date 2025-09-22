from sqlalchemy.orm import Session
from repositories.image import ImageRepository
from schemas.image import ImageUpload, ImageResponse
from schemas.auth import UserResponse
from services.cloudinary import CloudinaryService
from fastapi import UploadFile, HTTPException, status
from services.event import EventService

import insightface
import numpy as np
import cv2
import io
from sklearn.metrics.pairwise import cosine_similarity
from pathlib import Path

class ImageService:
    def __init__(self, db = Session):
        self.repo = ImageRepository(db)
        self.event_service = EventService(db)
        # Initialize InsightFace models
        # Get the absolute path to the 'ml_models' directory relative to the current file
        model_root_path = Path(__file__).parent.parent / "insightface"
        self.detector = insightface.app.FaceAnalysis(name='buffalo_l', root=str(model_root_path))
        self.detector.prepare(ctx_id=0, det_size=(640, 640))

    async def _process_image_for_faces(self, image_content: bytes):
        # Convert image bytes to numpy array
        np_image = np.frombuffer(image_content, np.uint8)
        img = cv2.imdecode(np_image, cv2.IMREAD_COLOR)

        if img is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Could not decode image")

        faces = self.detector.get(img)
        face_embeddings = []
        face_boxes = []

        for face in faces:
            embedding = face.embedding.tolist()
            bbox = face.bbox.astype(int).tolist()
            face_embeddings.append(embedding)
            face_boxes.append(bbox)
        return face_embeddings, face_boxes

    async def upload_images(self, images: list[UploadFile], event_id:int, user: UserResponse):
        self.event_service.get_event(event_id)
        result = []
        for image_file in images:
            image_content = await image_file.read()
            face_embeddings, face_boxes = await self._process_image_for_faces(image_content)
            
            # Reset file pointer after reading for face processing
            await image_file.seek(0)

            uploaded = await CloudinaryService.upload_image(image_file, user)
            data = ImageUpload(
                public_id=uploaded["public_id"],
                secure_url=uploaded["secure_url"],
                face_embeddings=face_embeddings,
                face_boxes=face_boxes,
            )
            db_image = self.repo.upload(event_id, user, data)
            image_response = ImageResponse(
                id=db_image.id,
                public_id=db_image.public_id,
                secure_url=db_image.secure_url,
                face_embeddings=db_image.face_embeddings,
                face_boxes=db_image.face_boxes,
                created_by=db_image.created_by
            )
            result.append(image_response)
        return result

    async def search_faces_in_event(
        self,
        event_id: int,
        user: UserResponse, # This 'user' is for authentication/authorization
        search_image: UploadFile,
    ) -> list[ImageResponse]:
        # 1. Process the search_image to get its face embeddings
        search_image_content = await search_image.read()
        search_face_embeddings, _ = await self._process_image_for_faces(search_image_content)

        if not search_face_embeddings:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="No face detected in the search image."
            )
        
        # Use the first detected face embedding for searching
        query_embedding = np.array(search_face_embeddings[0]).reshape(1, -1)

        # 2. Retrieve all images for the event that have face embeddings
        event_images_with_faces = self.repo.get_images_with_faces_by_event_id(event_id)

        matched_images = []
        similarity_threshold = 0.5 # Adjustable threshold

        for db_image in event_images_with_faces:
            if db_image.face_embeddings:
                for stored_embedding_list in db_image.face_embeddings:
                    stored_embedding = np.array(stored_embedding_list).reshape(1, -1)
                    similarity = cosine_similarity(query_embedding, stored_embedding)[0][0]

                    if similarity >= similarity_threshold:
                        matched_images.append(
                            ImageResponse(
                                id=db_image.id,
                                public_id=db_image.public_id,
                                secure_url=db_image.secure_url,
                                face_embeddings=db_image.face_embeddings,
                                face_boxes=db_image.face_boxes,
                                created_by=db_image.created_by
                            )
                        )
                        break # Move to the next image if a face matches
        return matched_images
