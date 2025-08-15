from fastapi import APIRouter, UploadFile, File, Depends
from services.cloudinary import CloudinaryService
from middleware.auth import get_current_admin
from typing import Annotated
from schemas.auth import UserResponse

router = APIRouter()

@router.post("/image")
async def upload_image(
    user: Annotated[UserResponse, Depends(get_current_admin)],  # ✅ ไม่มี default มาก่อน
    image_cover: UploadFile = File(...)  # ✅ มี default มาทีหลัง
):
    result = await CloudinaryService.upload_image(image_cover, user)
    return result

