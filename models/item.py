from core.base import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, Text, DECIMAL


class ItemDB(Base):
    __tablename__ = "items"
    
    id:Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title:Mapped[str] = mapped_column(String, index=True)
    description:Mapped[str] = mapped_column(Text, nullable=False)
    price:Mapped[float] = mapped_column(DECIMAL(10,2))
    
    def __repr__(self) -> str:
        return f"item(id={self.id!r}, title={self.title!r}, description={self.description!r}, price={self.price!r})"