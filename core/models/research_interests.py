from typing import TYPE_CHECKING

from sqlalchemy import String, ForeignKey, UUID, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base
from uuid import uuid4

if TYPE_CHECKING:
    from . import ResearchInterestsTeacher
    from . import Teachers


class ResearchInterests(Base):
    __tablename__ = "research_interests"
    uuid: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        primary_key=True,
        index=True,
        default=uuid4,
        server_default=text("uuid_generate_v4()"),
    )
    title: Mapped[str] = mapped_column(String(256), nullable=False, unique=True)
    teachers: Mapped[list["ResearchInterestsTeacher"]] = relationship(
        back_populates="research_interest"
    )
    teachers_viewonly: Mapped[list["Teachers"]] = relationship(
        back_populates="research_interest_viewonly",
        viewonly=True,
        secondary="research_interests_teachers",
    )
