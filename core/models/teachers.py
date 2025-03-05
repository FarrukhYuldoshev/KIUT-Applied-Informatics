from typing import TYPE_CHECKING
from sqlalchemy import String, JSON, Column, UUID, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from . import Base
from .enumrators import Roles, Languages
from uuid import uuid4

if TYPE_CHECKING:
    from . import Publications
    from . import ResearchInterestsTeacher
    from . import ResearchInterests
    from . import WorkExperience
    from . import Education
    from . import Publications
    from . import PublicationsTeacher


class Teachers(Base):
    __tablename__ = "teachers"
    uuid: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        primary_key=True,
        default=uuid4,
        server_default=text("uuid_generate_v4()"),
    )
    email: Mapped[str] = mapped_column(String(256), nullable=False, unique=True)
    image: Mapped[str] = mapped_column(String(100), nullable=True)
    scopus_link: Mapped[str] = mapped_column(String(256), nullable=True)
    translations: Mapped[dict[Languages, dict[str, str]]] = mapped_column(
        JSONB, default={}
    )
    publications: Mapped[list["PublicationsTeacher"]] = relationship(
        back_populates="teacher", cascade="all, delete-orphan"
    )
    publications_viewonly: Mapped[list["Publications"]] = relationship(
        back_populates="teachers_viewonly",
        secondary="publications_teachers",
        viewonly=True,
    )
    research_interests: Mapped[list["ResearchInterestsTeacher"]] = relationship(
        back_populates="teacher", cascade="all, delete-orphan"
    )
    research_interest_viewonly: Mapped[list["ResearchInterests"]] = relationship(
        back_populates="teachers_viewonly",
        viewonly=True,
        secondary="research_interests_teachers",
    )
    work_experiences: Mapped[list["WorkExperience"]] = relationship(
        back_populates="teacher",
        cascade="all, delete-orphan",
    )
    educations: Mapped[list["Education"]] = relationship(
        back_populates="teacher", cascade="all, delete-orphan"
    )
