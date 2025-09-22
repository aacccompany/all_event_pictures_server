from fastapi import APIRouter, Depends, UploadFile, File, Form
from schemas.image import ImageResponse, ImageUpload
from schemas.auth import UserResponse
from typing import Annotated
from middleware.auth import get_current_user, get_current_user_public
from sqlalchemy.orm import Session
from core.database import get_db
from services.image import ImageService

router = APIRouter()


@router.post("/upload-images/{event_id}", response_model=list[ImageResponse])
async def upload_images(
    event_id: int,
    user: Annotated[UserResponse, Depends(get_current_user)],
    images: list[UploadFile] = File(...),
    db: Session = Depends(get_db),
):
    return await ImageService(db).upload_images(images, event_id, user)

@router.post("/search-faces/{event_id}", response_model=list[ImageResponse])
async def search_faces(
    event_id: int,
    user: Annotated[UserResponse, Depends(get_current_user_public)],
    search_image: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    return await ImageService(db).search_faces_in_event(event_id, user, search_image)