from fastapi import UploadFile, HTTPException, status
from cloudinary.uploader import upload, destroy
from schemas.auth import UserResponse
from cloudinary.utils import cloudinary_url


class CloudinaryService:
    async def upload_image(image_cover: UploadFile, user: UserResponse, folder: str = "event-photo"):
        try:
            result = upload(image_cover.file, folder=folder)
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

    def get_watermarked_url(public_id: str):
        url, _ = cloudinary_url(
            public_id,
            transformation=[
                {
                    "overlay": {
                        "font_family": "Arial",
                        "font_size": 80,  
                        "text": "© AllEventPictures",
                    },
                    "color": "#FFFFFF",
                    "gravity": "center",
                    "flags": "tiled", 
                    "angle": -45, 
                    "opacity": 20, 
                }
            ],
        )
        return url

    async def upload_images(images: list[UploadFile], user: UserResponse, folder: str = "event-photo"):
        try:
            result = []
            for i in images:
                uploaded = await CloudinaryService.upload_image(i, user, folder=folder)
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
