from typing import TYPE_CHECKING
from uuid import uuid4
from sqlalchemy import UUID, text, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import mapped_column, Mapped, relationship
from .base import Base
from .enumrators import Languages

if TYPE_CHECKING:
    from . import AcademicPrograms


class Subjects(Base):
    __tablename__ = "subjects"
    uuid: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        primary_key=True,
        default=uuid4,
        server_default=text("uuid_generate_v4()"),
    )
    translations: Mapped[dict[Languages, dict[str, str]]] = mapped_column(
        JSONB, default={}  # fields: name, description,
    )
    credits: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    semester: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    academic_program_id: Mapped[str] = mapped_column(
        ForeignKey("academic_programs.uuid", ondelete="CASCADE"), nullable=False
    )
    academic_program: Mapped["AcademicPrograms"] = relationship(
        back_populates="subjects",
    )
