from fastapi import APIRouter
from controllers import cart_image, item, user, event, cloudinary, image, event_user, cart, bank_info, super_admin

root = APIRouter(
    prefix="/api/v1",
    dependencies=[]
)

root.include_router(item.router)
root.include_router(user.router)
root.include_router(event.router)
root.include_router(cloudinary.router)
root.include_router(image.router)
root.include_router(event_user.router)
root.include_router(cart.router)
root.include_router(cart_image.router)
root.include_router(bank_info.router)
root.include_router(super_admin.router)

