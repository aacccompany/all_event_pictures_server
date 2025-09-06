from core.base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, Boolean, DateTime, String, ForeignKey
from datetime import datetime, timezone


class CartDB(Base):
    __tablename__ = "cart"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    paymentStatus: Mapped[bool] = mapped_column(Boolean, default=False)
    downloaded: Mapped[bool] = mapped_column(Boolean, default=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc))

    created_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    updated_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_by: Mapped["UserDB"] = relationship("UserDB", foreign_keys=[created_by_id])
    updated_by: Mapped["UserDB"] = relationship("UserDB", foreign_keys=[updated_by_id])
    
    cart_images: Mapped[list["CartImageDB"]] = relationship(
        "CartImageDB", back_populates="cart", cascade="all, delete-orphan"
    )