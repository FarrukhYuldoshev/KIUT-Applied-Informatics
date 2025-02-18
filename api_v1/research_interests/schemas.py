from typing import Annotated, Optional, List
from pydantic import BaseModel, Field
import uuid as UUID
from api_v1.teachers.schemas import GetTeachersWithResearchInterests
import enum


class OrderingResearchInterests(enum.Enum):
    by_title = "title"
    by_most_used = "most_used"
    by_most_used_and_title = "most_used_and_title"


class OnlyUUID(BaseModel):
    uuid: UUID.UUID = Field(...)


class CreateResearchInterests(BaseModel):
    title: Annotated[
        str,
        Field(
            default="title",
            min_length=10,
            max_length=256,
            description="minimum 10 characters",
        ),
    ]


class GetResearchInterestsWithTeacher(CreateResearchInterests):
    uuid: UUID.UUID
    teachers_viewonly: Annotated[List[OnlyUUID], Field(serialization_alias="teachers")]


class GetResearchInterests(CreateResearchInterests):
    title: Optional[str] = None
    uuid: UUID.UUID
    count: Optional[int] = None


class GetResearchInterestsWithoutTeacher(BaseModel):
    title: Optional[str]
    uuid: UUID.UUID


class UpdateResearchInterests(CreateResearchInterests):
    pass


class DeleteResearchInterests(BaseModel):
    uuid: UUID.UUID


class CreatePublications(BaseModel):
    title: str
    link: Optional[str] = None
    teacher_id: str
