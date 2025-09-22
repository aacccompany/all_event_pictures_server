from core.base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime, timezone

class ImageDB(Base):
    __tablename__ = "images"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    public_id: Mapped[str] = mapped_column(String, index=True)
    secure_url: Mapped[str] = mapped_column(String, index=True)
    face_embeddings: Mapped[list[list[float]]] = mapped_column(JSONB, nullable=True)
    face_boxes: Mapped[list[list[float]]] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone.utc), default=datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone.utc), default=datetime.now(timezone.utc))
    deleted_at: Mapped[datetime] = mapped_column(DateTime(timezone.utc), nullable=True)

    created_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    updated_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_by: Mapped["UserDB"] = relationship("UserDB", foreign_keys=[created_by_id])
    updated_by: Mapped["UserDB"] = relationship("UserDB", foreign_keys=[updated_by_id])

    event_id: Mapped[int] = mapped_column(ForeignKey("events.id", ondelete="CASCADE"))
    event: Mapped["EventDB"] = relationship(back_populates="images")
    
    cart_images: Mapped[list["CartImageDB"]] = relationship(
        "CartImageDB", back_populates="image", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"ImageDB(id={self.id}, public_id={self.public_id}, secure_url={self.secure_url})"
