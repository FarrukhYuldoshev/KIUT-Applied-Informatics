from typing import TYPE_CHECKING
from sqlalchemy import UUID, text, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import mapped_column, Mapped, relationship
from uuid import uuid4
from . import Base
from datetime import date

from .enumrators import Languages

if TYPE_CHECKING:
    from . import Teachers


class Education(Base):
    __tablename__ = "education"
    uuid: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        server_default=text("uuid_generate_v4()"),
    )
    from_date: Mapped[date] = mapped_column(nullable=False)
    to_date: Mapped[date] = mapped_column(nullable=False)
    teacher_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), ForeignKey("teachers.uuid", ondelete="CASCADE")
    )
    translations: Mapped[dict[Languages, dict[str, str]]] = mapped_column(
        JSONB, default={}
    )
    teacher: Mapped["Teachers"] = relationship(back_populates="educations")
