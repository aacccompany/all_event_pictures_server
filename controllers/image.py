from fastapi import APIRouter, Depends, UploadFile, File, Form, WebSocket, WebSocketDisconnect
from schemas.image import ImageResponse, ImageManageGlobalResponse, ImageUpload, ImageIdList
from schemas.auth import UserResponse
from typing import Annotated
from middleware.auth import get_current_user, get_current_user_public
from sqlalchemy.orm import Session
from core.database import get_db
from services.image import ImageService
from utils.websocket import manager

router = APIRouter()

@router.websocket("/ws/{event_id}")
async def websocket_event_endpoint(websocket: WebSocket, event_id: int):
    await manager.connect(websocket, event_id)
    try:
        while True:
            # Keep connection alive
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, event_id)


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

@router.post("/internal/broadcast/{event_id}")
async def internal_broadcast(event_id: int, payload: dict):
    """
    Internal-only endpoint used by the Celery worker to trigger WebSockets.
    """
    await manager.broadcast(payload, event_id)
    return {"status": "broadcast_sent"}

@router.get("/manage/{event_id}", response_model=list[ImageResponse])
async def get_manage_images(
    event_id: int,
    user: Annotated[UserResponse, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    return await ImageService(db).get_managed_images_by_event(event_id, user)

@router.get("/manage/all/global", response_model=list[ImageManageGlobalResponse])
async def get_all_managed_images_global(
    user: Annotated[UserResponse, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    return await ImageService(db).get_all_managed_images(user)

@router.delete("/manage")
async def delete_manage_images(
    payload: ImageIdList,
    user: Annotated[UserResponse, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    return await ImageService(db).delete_managed_images(payload.image_ids, user)
