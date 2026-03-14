from sqlalchemy.orm import Session
from sqlalchemy import func
from repositories.event import EventRepository
from services.cloudinary import CloudinaryService
from models.cart_image import CartImageDB
from models.cart import CartDB
from models.image import ImageDB
from models.wallet import WalletTransactionDB, WalletTransactionType
from schemas.event import EventCreate, EventUpdate
from schemas.auth import UserResponse
from fastapi import HTTPException, status
from datetime import datetime


class EventService:
    def __init__(self, db = Session):
        self.repo = EventRepository(db)
        
    def create_event(self, event:EventCreate, user:UserResponse):
        return self.repo.create(event, user)
        
    def get_events(self, start_date: datetime = None, limit: int = None):
        events = self.repo.get_events_by_date_range_and_limit(start_date, limit)
        # Return an empty list instead of raising 404 so dashboards can show 0 safely
        return events

    def get_my_events(self, user: UserResponse, start_date: datetime = None, limit: int = None):
        events = self.repo.get_joined_events(user.id, start_date, limit)
        for event in events:
            # Query the user's images in this event
            user_images = self.repo.db.query(ImageDB.public_id).filter(
                ImageDB.event_id == event.id,
                ImageDB.created_by_id == user.id
            ).all()
            
            public_ids = [img[0] for img in user_images]
            earnings = 0
            if public_ids:
                descriptions = [f"Revenue from image sale: {pid}" for pid in public_ids]
                earnings_sum = self.repo.db.query(func.sum(WalletTransactionDB.amount)).filter(
                    WalletTransactionDB.user_id == user.id,
                    WalletTransactionDB.type == WalletTransactionType.EARNING,
                    WalletTransactionDB.description.in_(descriptions)
                ).scalar()
                if earnings_sum:
                    earnings = earnings_sum
            
            setattr(event, 'earnings', earnings / 100.0)
        return events
    
    def get_my_created_events(self, user: UserResponse, start_date: datetime = None, limit: int = None):
        events = self.repo.get_events_by_creator(user.id, start_date, limit)
        for event in events:
            expected_desc = f"Revenue from event image sale: {event.title}"
            earnings_sum = self.repo.db.query(func.sum(WalletTransactionDB.amount)).filter(
                WalletTransactionDB.user_id == user.id,
                WalletTransactionDB.type == WalletTransactionType.EARNING,
                WalletTransactionDB.description == expected_desc
            ).scalar()
            
            sales_count = self.repo.db.query(func.count(func.distinct(CartImageDB.cart_id))).join(
                ImageDB, CartImageDB.image_id == ImageDB.id
            ).join(
                CartDB, CartImageDB.cart_id == CartDB.id
            ).filter(
                ImageDB.event_id == event.id,
                CartDB.downloaded == True
            ).scalar()
            
            earnings = earnings_sum if earnings_sum else 0
            setattr(event, 'earnings', earnings / 100.0)
            setattr(event, 'sales_count', sales_count if sales_count else 0)
        return events

    def get_all_events_with_stats(self, start_date: datetime = None, limit: int = None):
        """Super-admin: all platform events enriched with sales_count and total earnings (100% Gross)."""
        events = self.repo.get_events_by_date_range_and_limit(start_date, limit)
        for event in events:
            # Count distinct completed cart checkouts that contain images from this event
            sales_count = self.repo.db.query(func.count(func.distinct(CartImageDB.cart_id))).join(
                ImageDB, CartImageDB.image_id == ImageDB.id
            ).join(
                CartDB, CartImageDB.cart_id == CartDB.id
            ).filter(
                ImageDB.event_id == event.id,
                CartDB.downloaded == True # This means it was paid and processed
            ).scalar() or 0

            # For Super Admin, "earnings" for an event row should be the Gross Sales (100%)
            # We calculate this by summing the counts of sold images from this event and multiplying by price
            # or joining with Transaction and summing the share.
            # Using price * count is safe since price is locked at event level (or fallback)
            
            # Get total images sold for this event
            sold_images_count = self.repo.db.query(func.count(CartImageDB.id)).join(
                ImageDB, CartImageDB.image_id == ImageDB.id
            ).join(
                CartDB, CartImageDB.cart_id == CartDB.id
            ).filter(
                ImageDB.event_id == event.id,
                CartDB.downloaded == True
            ).scalar() or 0

            price_satang = event.image_price if event.image_price is not None else 2000
            gross_earnings = (sold_images_count * price_satang) / 100.0

            setattr(event, 'sales_count', sales_count)
            setattr(event, 'earnings', gross_earnings)
        return events

    
    def get_event(self, event_id:int):
        event = self.repo.get_by_id(event_id)
        if not event:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Event ID {event_id} not found")
        return event
    
    def update_event(self, event_id: int, event: EventUpdate, user: UserResponse):
        db_event = self.repo.get_by_id(event_id)
        if not db_event:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Event ID {event_id} not found")
        
        if event.image_cover and db_event.public_id:
            CloudinaryService.delete_image(db_event.public_id)
        
        return self.repo.update(event_id, event, user)

    
    def remove_event(self, event_id:int):
        if not self.repo.get_by_id(event_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Event ID {event_id} not found")
        self.repo.remove(event_id)
        return {"message": f"Event ID {event_id} deleted"}
    
    def search_events(self, title:str):
        events = self.repo.search_by_title(title)
        return events
    
    def get_active_events(self):
        events = self.repo.get_active()
        if not events:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Events not found")
        return events
    
        
        