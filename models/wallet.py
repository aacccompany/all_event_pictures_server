from core.base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, DateTime, ForeignKey, Text
from datetime import datetime, timezone
import enum

class WalletTransactionType(str, enum.Enum):
    EARNING = "earning"
    WITHDRAWAL = "withdrawal"

class WithdrawalStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class WalletTransactionDB(Base):
    __tablename__ = "wallet_transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["UserDB"] = relationship("UserDB", foreign_keys=[user_id])
    
    amount: Mapped[int] = mapped_column(Integer) # Positive for earning, Negative for withdrawal
    type: Mapped[WalletTransactionType] = mapped_column(String)
    description: Mapped[str] = mapped_column(String)
    
    # Optional link to the source transaction (for earnings)
    related_transaction_id: Mapped[int | None] = mapped_column(ForeignKey("transactions.id"), nullable=True)
    related_transaction: Mapped["TransactionDB"] = relationship("TransactionDB", foreign_keys=[related_transaction_id])

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.now(timezone.utc)
    )

class WithdrawalRequestDB(Base):
    __tablename__ = "withdrawal_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["UserDB"] = relationship("UserDB", foreign_keys=[user_id])

    amount: Mapped[int] = mapped_column(Integer)
    status: Mapped[WithdrawalStatus] = mapped_column(String, default=WithdrawalStatus.PENDING)
    
    # Snapshot of bank info at the time of request
    bank_snapshot: Mapped[str] = mapped_column(Text) 

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc)
    )
