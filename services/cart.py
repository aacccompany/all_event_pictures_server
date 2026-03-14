import io, zipfile, requests
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from repositories.cart import CartRepository
import os
from sqlalchemy import func, or_, and_
from datetime import timedelta
from typing import List, Dict
from models.wallet import WalletTransactionDB, WalletTransactionType
from models.transaction import TransactionDB
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
            
            # Group images in this cart by (EventID, PhotographerID)
            groups = {} # (event_id, photographer_id) -> list of images
            for ci in cart.cart_images:
                if ci.image:
                    key = (ci.image.event_id, ci.image.created_by_id)
                    if key not in groups: groups[key] = []
                    groups[key].append(ci.image)

            buyer_name = cart.created_by.first_name if cart.created_by else "Guest"
            if cart.created_by and cart.created_by.last_name:
                buyer_name = f"{buyer_name} {cart.created_by.last_name}"
            buyer_email = cart.created_by.email if cart.created_by else None

            for (e_id, p_id), images in groups.items():
                first_img = images[0]
                event = first_img.event
                photographer = first_img.created_by
                organizer = event.created_by if event else None

                photo_count = len(images)
                price_satang = event.image_price if event and event.image_price is not None else 2000
                total_amount = (photo_count * price_satang) / 100.0

                # For Super Admin, we show the 50% Platform Share as requested
                earnings = total_amount * 0.50

                results.append({
                    "sale_id": cart.id,
                    "event_name": event.title if event else "N/A",
                    "photo_count": photo_count,
                    "purchased_at": cart.created_at,
                    "buyer_name": buyer_name,
                    "buyer_email": buyer_email,
                    "image_url": first_img.secure_url,
                    "total_amount": total_amount,
                    "earnings": earnings,
                    "role_split": "Platform Share (50%)",
                    "photographer_name": f"{photographer.first_name} {photographer.last_name}" if photographer else "N/A",
                    "organizer_name": f"{organizer.first_name} {organizer.last_name}" if organizer else "N/A"
                })
        return results

    def get_recent_sales_by_user(self, user_id: int, limit: int = 1000) -> List[Dict]:
        carts = self.cart_repo.get_recent_sales_by_identity(user_id, limit)
        results: List[Dict] = []
        for cart in carts:
            if not cart.cart_images:
                continue
            
            # Filter and Group images that belong to this user (Photographer) in this cart by Event
            event_groups = {} # event_id -> list of images
            for ci in cart.cart_images:
                if ci.image and ci.image.created_by_id == user_id:
                    e_id = ci.image.event_id
                    if e_id not in event_groups: event_groups[e_id] = []
                    event_groups[e_id].append(ci.image)
            
            if not event_groups:
                continue

            buyer_name = cart.created_by.first_name if cart.created_by else "Guest"
            if cart.created_by and cart.created_by.last_name:
                buyer_name = f"{buyer_name} {cart.created_by.last_name}"
            buyer_email = cart.created_by.email if cart.created_by else None

            for e_id, images in event_groups.items():
                first_img = images[0]
                event = first_img.event
                organizer = event.created_by if event else None

                photo_count = len(images)
                price_satang = event.image_price if event and event.image_price is not None else 2000
                total_amount = (photo_count * price_satang) / 100.0
                
                # Fetch consolidated earnings from wallet_transactions
                # Match by description containing the image's public_id (as used in WalletService)
                # However, since we consolidated, we should match by cart_id if possible.
                
                earnings_val = self.cart_repo.db.query(func.sum(WalletTransactionDB.amount)).join(
                    TransactionDB, WalletTransactionDB.related_transaction_id == TransactionDB.id
                ).filter(
                    WalletTransactionDB.user_id == user_id,
                    WalletTransactionDB.type == WalletTransactionType.EARNING,
                    or_(
                        TransactionDB.cart_id == cart.id,
                        and_(
                            TransactionDB.cart_id == None,
                            WalletTransactionDB.description.like(f"%{first_img.public_id}%")
                        )
                    )
                ).scalar()

                earnings = (earnings_val / 100.0) if earnings_val else 0.0

                results.append({
                    "sale_id": cart.id,
                    "event_name": event.title if event else "N/A",
                    "photo_count": photo_count,
                    "purchased_at": cart.created_at,
                    "buyer_name": buyer_name,
                    "buyer_email": buyer_email,
                    "image_url": first_img.secure_url,
                    "total_amount": total_amount,
                    "earnings": earnings,
                    "role_split": "Photographer (20%)",
                    "photographer_name": f"{first_img.created_by.first_name} {first_img.created_by.last_name}" if first_img.created_by else "You",
                    "organizer_name": f"{organizer.first_name} {organizer.last_name}" if organizer else "N/A"
                })
        return results
        
    def get_recent_sales_from_my_events(self, user_id: int, limit: int = 1000) -> List[Dict]:
        carts = self.cart_repo.get_recent_sales_by_event_creator(user_id, limit)
        results: List[Dict] = []
        for cart in carts:
            if not cart.cart_images:
                continue
            
            # Find images that belong to events created by this user (Organizer)
            # Group them by (EventID, PhotographerID)
            groups = {} # (event_id, photographer_id) -> list of images
            for ci in cart.cart_images:
                if ci.image and ci.image.event and ci.image.event.created_by_id == user_id:
                    key = (ci.image.event_id, ci.image.created_by_id)
                    if key not in groups: groups[key] = []
                    groups[key].append(ci.image)
            
            if not groups:
                continue

            buyer_name = cart.created_by.first_name if cart.created_by else "Guest"
            if cart.created_by and cart.created_by.last_name:
                buyer_name = f"{buyer_name} {cart.created_by.last_name}"
            buyer_email = cart.created_by.email if cart.created_by else None

            for (e_id, p_id), images in groups.items():
                first_img = images[0]
                event = first_img.event
                photographer = first_img.created_by

                photo_count = len(images)
                price_satang = event.image_price if event and event.image_price is not None else 2000
                total_amount = (photo_count * price_satang) / 100.0
                
                # Fetch consolidated earnings for the organizer for this event
                # Match by description containing the event title (as used in WalletService)
                # And strictly link via cart_id
                earnings_val = self.cart_repo.db.query(func.sum(WalletTransactionDB.amount)).join(
                    TransactionDB, WalletTransactionDB.related_transaction_id == TransactionDB.id
                ).filter(
                    WalletTransactionDB.user_id == user_id,
                    WalletTransactionDB.type == WalletTransactionType.EARNING,
                    or_(
                        TransactionDB.cart_id == cart.id,
                        and_(
                            TransactionDB.cart_id == None,
                            WalletTransactionDB.description.like(f"%{event.title}%")
                        )
                    )
                ).scalar()
                
                earnings = (earnings_val / 100.0) if earnings_val else 0.0

                results.append({
                    "sale_id": cart.id,
                    "event_name": event.title,
                    "photo_count": photo_count,
                    "purchased_at": cart.created_at,
                    "buyer_name": buyer_name,
                    "buyer_email": buyer_email,
                    "image_url": first_img.secure_url,
                    "total_amount": total_amount,
                    "earnings": earnings,
                    "role_split": "Organizer (30%)",
                    "photographer_name": f"{photographer.first_name} {photographer.last_name}" if photographer else "N/A",
                    "organizer_name": "You"
                })
        return results
        

    

