from sqlalchemy.orm import Session
from repositories.image import ImageRepository
from schemas.image import ImageUpload, ImageResponse
from schemas.auth import UserResponse
from services.cloudinary import CloudinaryService
from fastapi import UploadFile, HTTPException, status, BackgroundTasks
from services.event import EventService

from utils.websocket import manager
from worker import process_ai_background_task

import insightface
import numpy as np
import cv2
import io
import logging
import asyncio

from sklearn.metrics.pairwise import cosine_similarity
from pathlib import Path

# Initialize InsightFace model globally to avoid loading on every request
model_root_path = Path(__file__).parent.parent / "insightface"
face_detector = insightface.app.FaceAnalysis(name='buffalo_l', root=str(model_root_path))
face_detector.prepare(ctx_id=0, det_size=(640, 640))

class ImageService:
    def __init__(self, db = Session):
        self.repo = ImageRepository(db)
        self.event_service = EventService(db)

    async def _process_image_for_faces(self, image_content: bytes):
        # Convert image bytes to numpy array
        np_image = np.frombuffer(image_content, np.uint8)
        img = cv2.imdecode(np_image, cv2.IMREAD_COLOR)

        if img is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Could not decode image")

        # Use asyncio.to_thread to run the CPU-intensive FaceAnalysis in a background thread
        faces = await asyncio.to_thread(face_detector.get, img)
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
        
        async def process_single_image(image_file: UploadFile):
            uploaded = await CloudinaryService.upload_image(image_file, user, folder="event-photo/face-search")
            data = ImageUpload(
                public_id=uploaded["public_id"],
                secure_url=uploaded["secure_url"],
            )
            # image status is PENDING_AI by default
            db_image = self.repo.upload(event_id, user, data)
            
            # Queue background processing to Celery Redis
            process_ai_background_task.delay(db_image.id, db_image.secure_url, event_id)

            return ImageResponse(
                id=db_image.id,
                public_id=db_image.public_id,
                secure_url=db_image.secure_url,
                face_embeddings=db_image.face_embeddings,
                face_boxes=db_image.face_boxes,
                status=db_image.status,
                created_by=db_image.created_by
            )

        tasks = [process_single_image(img) for img in images]
        result = await asyncio.gather(*tasks)
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
        similarity_threshold = 0.35 # Adjustable threshold
        image_similarities = {} # Dictionary to store all similarities for each image ID

        for db_image in event_images_with_faces:
            if db_image.face_embeddings:
                image_similarities[db_image.id] = [] # Initialize list for current image
                for stored_embedding_list in db_image.face_embeddings:
                    stored_embedding = np.array(stored_embedding_list).reshape(1, -1)
                    similarity = cosine_similarity(query_embedding, stored_embedding)[0][0]
                    image_similarities[db_image.id].append(similarity)
                    
                    if similarity >= similarity_threshold:
                        matched_images.append(
                            ImageResponse(
                                id=db_image.id,
                                public_id=db_image.public_id,
                                secure_url=db_image.secure_url,
                                face_embeddings=db_image.face_embeddings,
                                face_boxes=db_image.face_boxes,
                                status=db_image.status,
                                created_by=db_image.created_by
                            )
                        )
                        break # Move to the next image if a face matches

                # Log max and min similarities for the current image ID
                if db_image.id in image_similarities and image_similarities[db_image.id]:
                    max_similarity = max(image_similarities[db_image.id])

                    max_accuracy_percentage = max_similarity * 100
                    max_distance = 1 - max_similarity

                    logging.info(f"Face search (Image ID: {db_image.id}) - Max Accuracy: {max_accuracy_percentage:.2f}%, Max Distance: {max_distance:.4f}")

        return matched_images

    async def get_managed_images_by_event(self, event_id: int, user: UserResponse):
        event = self.event_service.get_event(event_id)
        if user.role == "admin" and event.created_by_id != user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to manage images for this event")
        
        # Super-admin always returns all images by event.
        # User (Photographer) returns only their own images (repository logic)
        db_images = self.repo.get_images_by_event_and_role(event_id, user)
        
        result = [
            ImageResponse(
                id=db_image.id,
                public_id=db_image.public_id,
                secure_url=db_image.secure_url,
                face_embeddings=None, # Exclude for lightweight response
                face_boxes=None, 
                status=db_image.status,
                created_by=db_image.created_by
            ) for db_image in db_images
        ]
        return result

    async def get_all_managed_images(self, user: UserResponse):
        from schemas.image import ImageManageGlobalResponse
        db_images = self.repo.get_all_images_by_role(user)
        
        result = [
            ImageManageGlobalResponse(
                id=db_image.id,
                public_id=db_image.public_id,
                secure_url=db_image.secure_url,
                face_embeddings=None,
                face_boxes=None,
                status=db_image.status,
                created_by=db_image.created_by,
                event_id=db_image.event_id,
                event_name=db_image.event.title if db_image.event else "Unknown Event"
            ) for db_image in db_images
        ]
        return result

    async def delete_managed_images(self, image_ids: list[int], user: UserResponse):
        db_images = self.repo.get_images_by_ids(image_ids)
        if not db_images:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No images found for the provided IDs")
            
        allowed_image_ids_to_delete = []
        public_ids_to_delete = []

        for img in db_images:
            allowed = False
            if user.role == "super-admin":
                allowed = True
            elif user.role == "admin":
                # Check if admin is the event creator
                event = self.event_service.get_event(img.event_id)
                if event.created_by_id == user.id:
                    allowed = True
            elif user.role in ["user", "user-public"]:
                if img.created_by_id == user.id:
                    allowed = True

            if allowed:
                allowed_image_ids_to_delete.append(img.id)
                public_ids_to_delete.append(img.public_id)

        if not allowed_image_ids_to_delete:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to delete these images")

        # Delete from Cloudinary in parallel
        if public_ids_to_delete:
            delete_tasks = [CloudinaryService.delete_image(pid) for pid in public_ids_to_delete]
            await asyncio.gather(*delete_tasks, return_exceptions=True)
                
        # Delete from Database
        self.repo.delete_images(allowed_image_ids_to_delete)
        return {"message": f"Successfully deleted {len(allowed_image_ids_to_delete)} images", "deleted_ids": allowed_image_ids_to_delete}
