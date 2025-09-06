from core.base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, ForeignKey, DateTime
from datetime import datetime, timezone

class CartImageDB(Base):
    __tablename__ = "cart_images"
    
    id:Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    cart_id: Mapped[int] = mapped_column(ForeignKey("cart.id", ondelete="CASCADE"))
    cart: Mapped["CartDB"] = relationship("CartDB", back_populates="cart_images")
    
    image_id: Mapped[int] = mapped_column(ForeignKey("images.id", ondelete="CASCADE"))
    image: Mapped["ImageDB"] = relationship("ImageDB", back_populates="cart_images")
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc))