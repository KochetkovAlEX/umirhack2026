from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Content(Base):
    __tablename__ = "content"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    source: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    source_type: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    category: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    title: Mapped[str] = mapped_column(String(500), nullable=True, unique=True)
    text: Mapped[str] = mapped_column(Text, nullable=True)
    url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    views: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    likes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    comments_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    activity: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    comments: Mapped[Optional[list[str]]] = mapped_column(JSONB, nullable=True)
    city: Mapped[str] = mapped_column(Text, nullable=True)


class SummurizedContent(Base):
    __tablename__ = "summurized content"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    source: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    source_type: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    category: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    title: Mapped[str] = mapped_column(String(500), nullable=True, unique=True)
    text: Mapped[str] = mapped_column(Text, nullable=True)
    url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    views: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    likes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    comments_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    activity: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    comments: Mapped[Optional[list[str]]] = mapped_column(JSONB, nullable=True)
    city: Mapped[str] = mapped_column(Text, nullable=True)
    content_id: Mapped[int] = mapped_column(ForeignKey("content.id"))
