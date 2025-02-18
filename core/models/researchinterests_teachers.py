from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, UUID, UniqueConstraint
from sqlalchemy.orm import mapped_column, Mapped, relationship
from . import Base

if TYPE_CHECKING:
    from .research_interests import ResearchInterests
    from .teachers import Teachers


class ResearchInterestsTeacher(Base):
    __tablename__ = "research_interests_teachers"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    teacher_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "teachers.uuid",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    research_interests_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "research_interests.uuid",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    research_interest: Mapped["ResearchInterests"] = relationship(
        back_populates="teachers"
    )
    teacher: Mapped["Teachers"] = relationship(back_populates="research_interests")
    __table_args__ = (
        UniqueConstraint(
            "research_interests_id", "teacher_id", name="research_interests_teacher_unx"
        ),
    )
