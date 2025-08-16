from fastapi import UploadFile, HTTPException, status
from cloudinary.uploader import upload, destroy
from schemas.auth import UserResponse


class CloudinaryService:
    async def upload_image(image_cover: UploadFile, user: UserResponse):
        try:
            result = upload(image_cover.file, folder="event-photo")
            return {
                "public_id": result["public_id"],
                "secure_url": result["secure_url"],
                "created_by": user,
            }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error uploading image: {str(e)}",
            )

    async def upload_images(images: list[UploadFile], user: UserResponse):
        try:
            result = []
            for i in images:
                uploaded = await CloudinaryService.upload_image(i, user)
                result.append(uploaded)
            return result
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error Uploading images: {str(e)}",
            )
            
    async def delete_image(public_id: str):
        try:
            destroy(public_id)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error deleting image: {str(e)}",
            )
            
