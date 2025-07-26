from fastapi import UploadFile, HTTPException, status
from cloudinary.uploader import upload
from schemas.auth import UserResponse
class CloudinaryService:
    async def upload_image(image: UploadFile, user:UserResponse):
        try:
            result = upload(image.file, folder="event-photo")
            return {
                "public_id": result["public_id"],
                "secure_url": result["secure_url"],
                "created_by": user
                
            }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error uploading images: {str(e)}"
            )
