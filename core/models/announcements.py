from typing import List
from sqlalchemy import UUID, text, String, Text, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import mapped_column, Mapped
from uuid import uuid4
from .base import Base
import datetime


class Announcements(Base):
    __tablename__ = "announcements"
    uuid: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        server_default=text("uuid_generate_v4()"),
    )
    title: Mapped[str] = mapped_column(String(256), nullable=False)
    description: Mapped[str] = mapped_column(Text(), nullable=False)
    images: Mapped[List[str]] = mapped_column(JSONB, nullable=False, default=[])
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(), default=datetime.datetime.now(), nullable=False
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(),
        default=datetime.datetime.now(),
        onupdate=datetime.datetime.now(),
        nullable=False,
    )
