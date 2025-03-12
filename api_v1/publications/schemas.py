from fastapi import Form
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Annotated, Optional
from uuid import UUID as UUID4
from core.models.enumrators import Roles


class OnlyUUID(BaseModel):
    uuid: UUID4
    model_config = ConfigDict(from_attributes=True)


class GetTeachers(BaseModel):
    teacher_id: Annotated[
        UUID4, Field(default=..., alias="uuid", serialization_alias="teacher_id")
    ]
    email: Annotated[EmailStr, Field(...)]


class CreatePublication:
    def __init__(
        self,
        title: Annotated[str, Form(details="The title of publication")],
        link: Annotated[
            str,
            Form(
                description="link of the publication (not necessary)",
            ),
        ] = "",
        pre_print_link: Annotated[
            str,
            Form(
                description="Pre-print link of the publication (not necessary)",
            ),
        ] = "",
    ):
        self.title = title
        self.link = link
        self.pre_print_link = pre_print_link


class GetPublication(BaseModel):
    uuid: UUID4
    title: str
    link: Optional[str] = None
    pre_print_link: Optional[str] = None
    teachers_viewonly: Optional[list[OnlyUUID]] = Field(
        default=None, serialization_alias="teachers", alias="teachers_viewonly"
    )
    model_config = ConfigDict(from_attributes=True)


class UpdatePublication(BaseModel):
    title: str | None = None
    link: str | None = None
    pre_print_link: str | None = None


class GetPublicationWithoutTeacher(BaseModel):
    uuid: UUID4
    title: str
    link: Optional[str] = None
    pre_print_link: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class TeacherWithPublications(GetTeachers):
    publications_viewonly: Annotated[
        list[GetPublicationWithoutTeacher], Field(serialization_alias="publications")
    ]
