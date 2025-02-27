from typing import Annotated, Optional, List
from pydantic import BaseModel, Field
import uuid as UUID
from api_v1.teachers.schemas import GetTeachersWithResearchInterests
import enum
from fastapi import Form, Query
from core.models.enumrators import Languages


class OrderingResearchInterests(enum.Enum):
    by_title = "title"
    by_most_used = "most_used"
    by_most_used_and_title = "most_used_and_title"


class OnlyUUID(BaseModel):
    uuid: UUID.UUID = Field(...)


class CreateResearchInterests:
    def __init__(
        self,
        lang: Annotated[Languages, Query(..., alias="lang")],
        title: Annotated[
            List[str],
            Form(
                max_length=256,
                description="minimum 10 characters",
            ),
        ] = ["title"],
    ):
        self.title = title
        self.lang = lang


class GetResearchInterestsWithTeacher(BaseModel):
    uuid: UUID.UUID
    teachers_viewonly: Annotated[List[OnlyUUID], Field(serialization_alias="teachers")]


class GetResearchInterests(BaseModel):
    title: Optional[str] = None
    uuid: UUID.UUID
    in_teacher_count: Optional[int] = None


class GetResearchInterestsWithoutTeacher(BaseModel):
    title: Optional[str]
    uuid: UUID.UUID


class UpdateResearchInterests(BaseModel):
    pass


class DeleteResearchInterests(BaseModel):
    uuid: UUID.UUID


class CreatePublications(BaseModel):
    title: str
    link: Optional[str] = None
    teacher_id: str
