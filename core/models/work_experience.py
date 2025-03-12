from typing import TYPE_CHECKING
from sqlalchemy import UUID, text, String, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import mapped_column, Mapped, relationship
from uuid import uuid4
from . import Base
from datetime import date

from .enumrators import Languages

if TYPE_CHECKING:
    from . import Teachers


class WorkExperience(Base):
    __tablename__ = "work_experience"
    uuid: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        server_default=text("uuid_generate_v4()"),
    )
    from_date: Mapped[date] = mapped_column(nullable=False)
    to_date: Mapped[date] = mapped_column(nullable=False)
    teacher_id: Mapped[str] = mapped_column(ForeignKey("teachers.uuid"))
    translations: Mapped[dict[Languages, dict[str, str]]] = mapped_column(
        MutableDict.as_mutable(JSONB), default={}
    )
    teacher: Mapped[list["Teachers"]] = relationship(back_populates="work_experiences")
    # __table_args__ = (
    #     UniqueConstraint(
    #         "place", "role", "teacher_id", name="work_experience_title_teacher_id_uidx"
    #     ),
    # )
