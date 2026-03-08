import io, zipfile, requests
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from repositories.cart import CartRepository
import os
from sqlalchemy import func
from datetime import timedelta
from typing import List, Dict
from models.wallet import WalletTransactionDB, WalletTransactionType
from schemas.download_history import DownloadHistoryResponse, DownloadHistoryImageResponse


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
            expiration_date = purchase_date + timedelta(days=60)
            
            image_responses = []
            for ci in cart.cart_images:
                if ci.image:
                    image_responses.append(
                        DownloadHistoryImageResponse(
                            id=ci.image.id,
                            secure_url=ci.image.secure_url,
                            public_id=ci.image.public_id
                        )
                    )

            history_list.append(
                DownloadHistoryResponse(
                    id=cart.id,
                    event_name=event_name,
                    number_of_files=number_of_files,
                    purchase_date=purchase_date,
                    expiration_date=expiration_date,
                    images=image_responses
                )
            )
        return history_list
    
    def get_recent_sales(self, limit: int = 1000) -> List[Dict]:
        carts = self.cart_repo.recent_downloaded_carts(limit)
        results: List[Dict] = []
        for cart in carts:
            if not cart.cart_images:
                continue
            # ใช้อีเวนต์จากรูปแรกในตะกร้า (ทุกภาพในตะกร้าเดียวกันควรเป็นอีเวนต์เดียวกัน)
            first_image = cart.cart_images[0].image if cart.cart_images[0] else None
            event = getattr(first_image, "event", None)
            if not event:
                continue
            
            image_url = first_image.secure_url if first_image else None
            
            buyer_name = cart.created_by.first_name if cart.created_by else None
            if cart.created_by and cart.created_by.last_name:
                buyer_name = f"{buyer_name} {cart.created_by.last_name}" if buyer_name else cart.created_by.last_name
            buyer_email = cart.created_by.email if cart.created_by else None

            photo_count = len(cart.cart_images)
            price_satang = event.image_price if event.image_price is not None else 2000
            total_amount = (photo_count * price_satang) / 100.0
            earnings = total_amount

            results.append({
                "sale_id": cart.id,
                "event_name": event.title,
                "photo_count": photo_count,
                "purchased_at": cart.created_at,
                "buyer_name": buyer_name,
                "buyer_email": buyer_email,
                "image_url": image_url,
                "total_amount": total_amount,
                "earnings": earnings,
                "role_split": "Total Revenue"
            })
        return results

    def get_recent_sales_by_user(self, user_id: int, limit: int = 1000) -> List[Dict]:
        carts = self.cart_repo.get_recent_sales_by_identity(user_id, limit)
        results: List[Dict] = []
        for cart in carts:
            if not cart.cart_images:
                continue
            
            # Filter images that belong to this user
            user_images = [ci.image for ci in cart.cart_images if ci.image and ci.image.created_by_id == user_id]
            
            if not user_images:
                continue
            
            # Use the first image representing the user's sale in this cart
            first_image = user_images[0]
            event = getattr(first_image, "event", None)
            
            if not event:
                continue

            image_url = first_image.secure_url if first_image else None

            buyer_name = cart.created_by.first_name if cart.created_by else None
            if cart.created_by and cart.created_by.last_name:
                buyer_name = f"{buyer_name} {cart.created_by.last_name}" if buyer_name else cart.created_by.last_name
            buyer_email = cart.created_by.email if cart.created_by else None

            photo_count = len(user_images)
            price_satang = event.image_price if event.image_price is not None else 2000
            total_amount = (photo_count * price_satang) / 100.0
            
            # Query actual wallet earning for this specific user/cart/images
            public_ids = [img.public_id for img in user_images if img and img.public_id]
            earnings_sum = 0
            if public_ids:
                descriptions = [f"Revenue from image sale: {pid}" for pid in public_ids]
                earnings_val = self.cart_repo.db.query(func.sum(WalletTransactionDB.amount)).filter(
                    WalletTransactionDB.user_id == user_id,
                    WalletTransactionDB.type == WalletTransactionType.EARNING,
                    WalletTransactionDB.description.in_(descriptions)
                ).scalar()
                if earnings_val:
                    earnings_sum = earnings_val

            earnings = earnings_sum / 100.0

            results.append({
                "sale_id": cart.id,
                "event_name": event.title,
                "photo_count": photo_count,
                "purchased_at": cart.created_at,
                "buyer_name": buyer_name,
                "buyer_email": buyer_email,
                "image_url": image_url,
                "total_amount": total_amount,
                "earnings": earnings,
                "role_split": "Photographer (20%)",
            })
        return results
        
    def get_recent_sales_from_my_events(self, user_id: int, limit: int = 1000) -> List[Dict]:
        carts = self.cart_repo.get_recent_sales_by_event_creator(user_id, limit)
        results: List[Dict] = []
        for cart in carts:
            if not cart.cart_images:
                continue
            
            # Find images that belong to events created by this user
            relevant_images = []
            for ci in cart.cart_images:
                if ci.image and ci.image.event and ci.image.event.created_by_id == user_id:
                    relevant_images.append(ci.image)
            
            if not relevant_images:
                continue
                
            first_relevant_image = relevant_images[0]
            target_event = first_relevant_image.event
            photo_count = len(relevant_images)
            image_url = first_relevant_image.secure_url

            buyer_name = cart.created_by.first_name if cart.created_by else None
            if cart.created_by and cart.created_by.last_name:
                buyer_name = f"{buyer_name} {cart.created_by.last_name}" if buyer_name else cart.created_by.last_name
            buyer_email = cart.created_by.email if cart.created_by else None

            price_satang = target_event.image_price if target_event.image_price is not None else 2000
            total_amount = (photo_count * price_satang) / 100.0
            
            # Note: The WalletService adds EXACTLY one earning entry per event per transaction for organizers.
            # To be entirely precise we calculate the earning of the organizer for this cart event.
            # Easiest way right now is just matching the expected earning if it exists.
            
            # For organizers, it's 30% of total
            expected_desc = f"Revenue from event image sale: {target_event.title}"
            # Because this gets tricky to map exactly to the CART without tx_id, we check if the wallet
            # has earnings. For detailed sales, since we don't have perfect transaction mapping
            # available efficiently from Cart -> Tx right now, we will query the wallet. 
            # If the user has NO balance for this event at all, it's 0.
            
            earnings_val = self.cart_repo.db.query(func.sum(WalletTransactionDB.amount)).filter(
                WalletTransactionDB.user_id == user_id,
                WalletTransactionDB.type == WalletTransactionType.EARNING,
                WalletTransactionDB.description == expected_desc
            ).scalar()
            
            # If there's overall earning for the event, we assume this cart generated its 30% share, 
            # OTHERWISE, if there's no earning in the wallet at all, it generated 0.
            earnings = 0.0
            if earnings_val and earnings_val > 0:
                 earnings = (photo_count * int(price_satang * 0.30)) / 100.0

            results.append({
                "sale_id": cart.id,
                "event_name": target_event.title,
                "photo_count": photo_count,
                "purchased_at": cart.created_at,
                "buyer_name": buyer_name,
                "buyer_email": buyer_email,
                "image_url": image_url,
                "total_amount": total_amount,
                "earnings": earnings,
                "role_split": "Organizer (30%)",
            })
        return results
        

    

