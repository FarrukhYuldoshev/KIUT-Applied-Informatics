from typing import TYPE_CHECKING

from sqlalchemy import String, ForeignKey, UUID, text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base
from uuid import uuid4

if TYPE_CHECKING:
    from . import Teachers
    from . import PublicationsTeacher


class Publications(Base):
    __tablename__ = "publications"
    uuid: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        primary_key=True,
        default=uuid4,
        server_default=text("uuid_generate_v4()"),
    )
    title: Mapped[str] = mapped_column(String, nullable=False)
    link: Mapped[str] = mapped_column(String, nullable=True)
    pre_print_link: Mapped[str] = mapped_column(String, nullable=True)
    teachers: Mapped[list["PublicationsTeacher"]] = relationship(
        back_populates="publication", overlaps="publications_viewonly"
    )
    teachers_viewonly: Mapped[list["Teachers"]] = relationship(
        back_populates="publications_viewonly",
        secondary="publications_teachers",
        # viewonly=True,
    )

    def __str__(self):
        return f"Publications(#{self.uuid}, title: {self.title} pre_print_link: {self.pre_print_link}, link: {self.link})"
