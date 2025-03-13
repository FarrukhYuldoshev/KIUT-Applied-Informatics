from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import UUID, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import mapped_column, Mapped, relationship

from .base import Base
from .enumrators import Languages

if TYPE_CHECKING:
    from . import Subjects


class AcademicPrograms(Base):
    __tablename__ = "academic_programs"
    uuid: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        primary_key=True,
        default=uuid4,
        server_default=text("uuid_generate_v4()"),
    )
    translations: Mapped[dict[Languages, dict[str, str]]] = mapped_column(
        MutableDict.as_mutable(JSONB), default={}
    )
    year_of_study: Mapped[int] = mapped_column(nullable=False, default=1)
    subjects: Mapped[list["Subjects"]] = relationship(
        back_populates="academic_program",
    )

    def __str__(self):
        return f"Academic Program: #{self.uuid}, title: {self.translations.get(Languages.en, {}).get('title')}"
