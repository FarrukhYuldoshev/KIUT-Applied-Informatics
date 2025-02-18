from typing import TYPE_CHECKING

from sqlalchemy import UUID, text, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import mapped_column, Mapped, relationship
from uuid import uuid4
from . import Base
from datetime import date
from .enumrators import Degrees

if TYPE_CHECKING:
    from . import Teachers


class Education(Base):
    __tablename__ = "education"
    uuid: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        server_default=text("uuid_generate_v4()"),
        index=True,
    )
    place: Mapped[str] = mapped_column(String(1024), nullable=False)
    degree: Mapped[Degrees] = mapped_column(nullable=False)
    from_date: Mapped[date] = mapped_column(nullable=False)
    to_date: Mapped[date] = mapped_column(nullable=False)
    teacher_id: Mapped[str] = mapped_column(
        ForeignKey("teachers.uuid", ondelete="CASCADE")
    )
    teacher: Mapped["Teachers"] = relationship(back_populates="educations")
    __table_args__ = (
        UniqueConstraint(
            "place", "teacher_id", "degree", name="educations_title_teacher_id_uidx"
        ),
    )
