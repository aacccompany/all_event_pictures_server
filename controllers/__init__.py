from fastapi import APIRouter
from controllers import item, user, event, cloudinary

root = APIRouter(
    prefix="/api/v1",
    dependencies=[]
)

root.include_router(item.router)
root.include_router(user.router)
root.include_router(event.router)
root.include_router(cloudinary.router)

