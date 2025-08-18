from core.base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String,Text, Boolean, Date, DateTime, ForeignKey
import datetime
from datetime import datetime, timezone
from typing import List

class EventDB(Base):
    __tablename__ = "events"
    
    id:Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title:Mapped[str] = mapped_column(String, index=True)
    image_cover:Mapped[str] = mapped_column(String, index=True)
    public_id:Mapped[str] = mapped_column(String, index=True)
    date: Mapped[datetime.date] = mapped_column(Date, nullable=True)
    description:Mapped[str] = mapped_column(Text, nullable=True)
    location:Mapped[str] = mapped_column(String, nullable=True)
    active:Mapped[bool] = mapped_column(Boolean, default=False)
    event_type:Mapped[str] = mapped_column(String)
    limit:Mapped[int] = mapped_column(Integer, nullable=True)
    joined_count:Mapped[int] = mapped_column(Integer, default=0)
    created_at:Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    updated_at:Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    deleted_at:Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_by_id:Mapped[int] = mapped_column(ForeignKey("users.id"))
    updated_by_id:Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_by:Mapped["UserDB"] = relationship("UserDB", foreign_keys=[created_by_id])
    updated_by:Mapped["UserDB"] = relationship("UserDB", foreign_keys=[updated_by_id])
    images:Mapped[List["ImageDB"]] = relationship(back_populates="event", cascade="all, delete-orphan", passive_deletes=True)
    event_users:Mapped[List["EventUserDB"]] = relationship(back_populates="event", cascade="all, delete-orphan", passive_deletes=True)
    
    def __repr__(self):
        return f"""Events(id={self.id!r}, title={self.title!r}, image_cover={self.image_cover!r}, date={self.date!r}, 
                description={self.description!r}, location={self.location!r}, active={self.active})"""
    