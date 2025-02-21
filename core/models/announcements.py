from typing import List
from sqlalchemy import UUID, text, String, Text, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import mapped_column, Mapped
from uuid import uuid4
from .base import Base
import datetime
from .enumrators import Languages


class Announcements(Base):
    __tablename__ = "announcements"
    uuid: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        server_default=text("uuid_generate_v4()"),
    )
    images: Mapped[List[str]] = mapped_column(JSONB, nullable=False, default=[])
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(), default=datetime.datetime.now(), nullable=False
    )
    translations: Mapped[dict[Languages, dict[str, str]]] = mapped_column(
        JSONB, nullable=False, default={}
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(),
        default=datetime.datetime.now(),
        onupdate=datetime.datetime.now(),
        nullable=False,
    )
