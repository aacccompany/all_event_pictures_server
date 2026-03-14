from core.base import Base
from models.cart import CartDB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, DateTime, ForeignKey, Enum
from datetime import datetime, timezone
import enum

class TransactionStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"

class TransactionDB(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    stripe_session_id: Mapped[str] = mapped_column(String, unique=True, index=True)
    amount: Mapped[int] = mapped_column(Integer) # Amount in satang/cents
    status: Mapped[TransactionStatus] = mapped_column(String, default=TransactionStatus.PENDING)
    
    payer_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    payer: Mapped["UserDB"] = relationship("UserDB", foreign_keys=[payer_id])

    cart_id: Mapped[int | None] = mapped_column(ForeignKey("cart.id"), nullable=True)
    cart: Mapped["CartDB"] = relationship("CartDB", foreign_keys=[cart_id])

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc)
    )
