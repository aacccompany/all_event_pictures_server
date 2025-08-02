from fastapi import APIRouter, Depends, UploadFile, File, Form
from schemas.image import ImageResponse, ImageUpload
from schemas.auth import UserResponse
from typing import Annotated
from middleware.auth import get_current_user
from sqlalchemy.orm import Session
from core.database import get_db
from services.image import ImageService

router = APIRouter()


@router.post("/upload-images", response_model=list[ImageResponse])
async def upload_images(
    user: Annotated[UserResponse, Depends(get_current_user)],
    images: list[UploadFile] = File(...),
    event_id: int = Form(...),
    db: Session = Depends(get_db),
):
    return await ImageService(db).upload_images(images, event_id, user)
