import io, zipfile, requests
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from repositories.cart import CartRepository
import os
from schemas.download_history import DownloadHistoryResponse


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
    
    def download_cart_zip_by_id(self, user_id: int, cart_id: int):
        cart = self.cart_repo.get_cart_by_id(user_id, cart_id)
        if not cart or not cart.cart_images:
            raise HTTPException(status_code=404, detail="Cart empty or not found")

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
        
        # ไม่ต้องตั้งค่า cart.downloaded = True อีกครั้ง เพราะถือว่าดาวน์โหลดไปแล้ว
        
        zip_buffer.seek(0)
        return zip_buffer, cart.id
    
    def get_my_images(self, user_id:int):
        images = self.cart_repo.my_images(user_id)
        if not images:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Your history not found")
        return images
        
    def get_download_history(self, user_id: int) -> list[DownloadHistoryResponse]:
        downloaded_carts = self.cart_repo.my_images(user_id)
        if not downloaded_carts:
            return []
        
        history_list = []
        for cart in downloaded_carts:
            event_name = None  # ตั้งเป็น None เพื่อตรวจสอบภายหลัง
            number_of_files = 0

            if cart.cart_images and cart.cart_images[0].image and cart.cart_images[0].image.event:
                event_name = cart.cart_images[0].image.event.title
                number_of_files = len(cart.cart_images)
            
            # กรองรายการที่ไม่มีข้อมูล Event Name หรือ Number of Files เป็น 0
            if event_name is None or number_of_files == 0:
                continue # ข้าม cart นี้ไป

            purchase_date = cart.created_at
            
            history_list.append(
                DownloadHistoryResponse(
                    id=cart.id,
                    event_name=event_name,
                    number_of_files=number_of_files,
                    purchase_date=purchase_date
                )
            )
        return history_list
        

    

