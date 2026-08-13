"""Embedded Power BI dashboard link model."""

from sqlalchemy import Boolean, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class PowerBILink(Base):
    __tablename__ = "powerbi_links"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    embed_url: Mapped[str] = mapped_column(String(2000), nullable=False)  # Power BI "Publish to web" or embed iframe URL
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    display_order: Mapped[int] = mapped_column(Integer, default=0)
