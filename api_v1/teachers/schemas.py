from typing import Annotated, Optional, Dict, Any, List

from fastapi import Form, File, UploadFile

from core.models.enumrators import Roles
from pydantic import BaseModel, Field, EmailStr
from uuid import UUID as UUID4
from api_v1.educations.schemas import GetEducationWithoutTeacher
from api_v1.publications.schemas import GetPublicationWithoutTeacher
from api_v1.work_experience.schemas import GetWorkExperienceWithoutTeacher


class OnlyUUID(BaseModel):
    uuid: UUID4 = Field(...)


class ResearchInterest(BaseModel):
    id: Annotated[UUID4, Field(alias="uuid")]
    title: str


class CreateTeacher:
    def __init__(
        self,
        full_name: Annotated[str, Form(..., min_length=5, max_length=256)],
        email: Annotated[EmailStr, Form(...)],
        role: Annotated[Roles, Form(...)],
        image: Annotated[UploadFile, File(description="Teacher's image")],
        scopus_link: Annotated[Optional[str], Form()] = "",
    ):
        self.full_name = full_name
        self.email = email
        self.role = role
        self.image = image
        self.scopus_link = scopus_link


class GetTeachers(BaseModel):
    teacher_id: Annotated[
        UUID4, Field(default=..., alias="uuid", serialization_alias="uuid")
    ]
    full_name: Annotated[str, Field(..., min_length=5, max_length=256)]
    email: Annotated[EmailStr, Field(...)]
    role: Annotated[Roles, Field(...)]
    scopus_link: Annotated[Optional[str], Field(None)]
    image: Annotated[str, Field(..., description="Teacher's image")]


class GetTeachersWithResearchInterests(GetTeachers):
    research_interest_viewonly: Annotated[
        List[ResearchInterest],
        Field(serialization_alias="research_interests"),
    ]
    publications_viewonly: Annotated[
        List["GetPublicationWithoutTeacher"], Field(serialization_alias="publications")
    ]
    work_experiences: Annotated[
        List["GetWorkExperienceWithoutTeacher"],
        Field(serialization_alias="work_experiences"),
    ]
    educations: Annotated[
        List["GetEducationWithoutTeacher"], Field(serialization_alias="educations")
    ]


class UpdateTeacher:
    def __init__(
        self,
        full_name: Optional[str] = Form(default="", max_length=256),
        email: Optional[str] = Form(default=None),
        role: Optional[str] = Form(default=""),
        scopus_link: Optional[str] = Form(default=""),
        image: UploadFile | str | None = File(None, media_type="image/*"),
    ):
        self.full_name = full_name
        self.email = email
        self.role = role
        self.scopus_link = scopus_link
        self.image = image
