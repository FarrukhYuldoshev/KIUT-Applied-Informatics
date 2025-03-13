from typing import TYPE_CHECKING
from sqlalchemy import func, ForeignKey, UUID, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from . import Base

if TYPE_CHECKING:
    from . import Teachers
    from . import Publications


class PublicationsTeacher(Base):
    __tablename__ = "publications_teachers"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    publication_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), ForeignKey("publications.uuid", ondelete="CASCADE")
    )
    teacher_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), ForeignKey("teachers.uuid", ondelete="CASCADE")
    )
    teacher: Mapped["Teachers"] = relationship(
        back_populates="publications", overlaps="publications_viewonly"
    )
    publication: Mapped["Publications"] = relationship(
        back_populates="teachers", overlaps="publications_viewonly"
    )
    __table_args__ = (UniqueConstraint("publication_id", "teacher_id"),)
