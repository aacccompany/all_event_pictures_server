import io, zipfile, requests
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from repositories.cart import CartRepository
import os


class CartService:
    def __init__(self, db: Session):
        self.cart_repo = CartRepository(db)

    def get_my_cart(self, user_id: int):
        cart = self.cart_repo.get_my_cart(user_id)
        if not cart:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cart not found"
            )
        return cart
    
    def download_cart_zip(self, user_id: int):
        cart = self.cart_repo.get_my_cart(user_id)
        if not cart or not cart.cart_images:
            raise HTTPException(status_code=404, detail="Cart empty")

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for ci in cart.cart_images:
                img_url = ci.image.secure_url
                try:
                    resp = requests.get(img_url, timeout=10)
                    resp.raise_for_status()
                except Exception:
                    continue 

                url_path = img_url.split("?")[0]
                ext = os.path.splitext(url_path)[1] or ".jpg"

                filename = f"{ci.id}_{ci.image.public_id.split('/')[-1]}{ext}"
                zip_file.writestr(filename, resp.content)
        cart.downloaded = True
        self.cart_repo.db.commit()
        self.cart_repo.db.refresh(cart)

        zip_buffer.seek(0)
        return zip_buffer, cart.id
    
    def get_my_images(self, user_id:int):
        images = self.cart_repo.my_images(user_id)
        if not images:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Your history not found")
        return images
        

    

