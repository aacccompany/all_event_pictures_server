import os
from celery import Celery
import insightface
import numpy as np
import cv2
import requests
import logging
from pathlib import Path
from core.database import SessionLocal
from repositories.image import ImageRepository
import models

# Initialize Celery App
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/1")

celery_app = Celery(
    "worker",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND
)

# Set up logging for celery worker
logging.basicConfig(level=logging.INFO)

# Global variables to hold model instances
face_detector = None

@celery_app.on_after_configure.connect
def setup_model(sender, **kwargs):
    """
    Load the AI model only once when the Celery worker starts.
    """
    global face_detector
    try:
        logging.info("Loading InsightFace Model...")
        model_root_path = Path(__file__).parent / "insightface"
        face_detector = insightface.app.FaceAnalysis(name='buffalo_l', root=str(model_root_path))
        face_detector.prepare(ctx_id=0, det_size=(640, 640))
        logging.info("InsightFace Model Loaded Successfully!")
    except Exception as e:
        logging.error(f"Failed to load InsightFace Model: {e}")

def _broadcast_to_fastapi(event_id: int, message_payload: dict):
    """
    Sends a webhook back to the FastAPI container so it can trigger websockets
    """
    # Using fastapi-app hostname since we run inside docker-compose
    fastapi_url = f"http://fastapi-app:8081/api/v1/internal/broadcast/{event_id}"
    try:
        requests.post(fastapi_url, json=message_payload, timeout=5)
    except Exception as e:
        logging.error(f"Failed to broadcast websocket to FastAPI: {e}")


@celery_app.task(name="process_ai_background", bind=True, max_retries=3)
def process_ai_background_task(self, image_id: int, image_url: str, event_id: int):
    """
    Celery task that downloads an image, processes faces via InsightFace, 
    and saves the embeddings to the DB.
    """
    global face_detector
    db = SessionLocal()
    try:
        logging.info(f"Task started for image_id={image_id}, event_id={event_id}")
        
        # 1. Download image from Cloudinary
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()
        
        # 2. Convert to CV2 Matrix
        np_image = np.frombuffer(response.content, np.uint8)
        img = cv2.imdecode(np_image, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError("Could not decode image from URL")

        # 3. Process AI
        # Note: We run this synchronously since we are already in a dedicated background worker
        faces = face_detector.get(img)
        
        face_embeddings = []
        face_boxes = []

        for face in faces:
            embedding = face.embedding.tolist()
            bbox = face.bbox.astype(int).tolist()
            face_embeddings.append(embedding)
            face_boxes.append(bbox)
            
        # 4. Save to Database
        repo = ImageRepository(db)
        repo.update_face_embeddings(image_id, face_embeddings, face_boxes)
        
        logging.info(f"Successfully processed image_id={image_id} - found {len(faces)} faces.")

        # 5. Broadcast Success to Websockets via FastAPI
        _broadcast_to_fastapi(event_id, {
            "type": "COMPLETED",
            "image_id": image_id,
            "status": "COMPLETED",
            "message": "AI Processing completed successfully"
        })
        
        return {"status": "success", "image_id": image_id, "faces_found": len(faces)}

    except Exception as exc:
        logging.error(f"Error processing image {image_id}: {exc}")
        
        # Broadcast FAILED state
        _broadcast_to_fastapi(event_id, {
            "type": "FAILED",
            "image_id": image_id,
            "status": "FAILED",
            "message": f"AI Processing failed"
        })
        
        # Optional: update DB to FAILED status
        try:
            repo = ImageRepository(db)
            db_image = repo.get_all([image_id])[0] if repo.get_all([image_id]) else None
            if db_image:
                db_image.status = "FAILED"
                db.commit()
        except Exception:
            pass

        # Retry the task for typical network failures
        raise self.retry(exc=exc, countdown=5)
    finally:
        db.close()
