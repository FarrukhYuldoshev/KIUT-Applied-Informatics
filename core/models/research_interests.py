from typing import TYPE_CHECKING

from sqlalchemy import UUID, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from . import Base
from uuid import uuid4
from .enumrators import Languages

if TYPE_CHECKING:
    from . import ResearchInterestsTeacher
    from . import Teachers


class ResearchInterests(Base):
    __tablename__ = "research_interests"
    uuid: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        primary_key=True,
        default=uuid4,
        server_default=text("uuid_generate_v4()"),
    )
    teachers: Mapped[list["ResearchInterestsTeacher"]] = relationship(
        back_populates="research_interest",
        cascade="all, delete-orphan",
    )
    translations: Mapped[dict[Languages, dict[str, str]]] = mapped_column(
        JSONB, default={}
    )
    teachers_viewonly: Mapped[list["Teachers"]] = relationship(
        back_populates="research_interest_viewonly",
        viewonly=True,
        secondary="research_interests_teachers",
    )
