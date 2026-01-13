from core.base import Base
from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

class BankInfoDB(Base):
    __tablename__ = "bank_infos"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), unique=True)
    
    bank_name: Mapped[str] = mapped_column(String, nullable=True)
    bank_branch: Mapped[str] = mapped_column(String, nullable=True)
    account_name: Mapped[str] = mapped_column(String, nullable=True)
    account_number: Mapped[str] = mapped_column(String, nullable=True)
    citizen_id: Mapped[str] = mapped_column(String, nullable=True)
    
    user = relationship("UserDB", back_populates="bank_info")
