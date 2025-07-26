from fastapi import APIRouter, UploadFile
from services.cloudinary import CloudinaryService
from fastapi import Depends
from middleware.auth import get_current_admin
from typing import Annotated
from schemas.auth import UserResponse

router = APIRouter()

@router.post("/image")
async def upload_image(image:UploadFile, user: Annotated[UserResponse, Depends(get_current_admin)]):
    result = await CloudinaryService.upload_image(image, user)
    return result
    