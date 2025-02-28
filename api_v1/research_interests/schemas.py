from typing import Annotated, Optional, List
from pydantic import BaseModel, Field, StringConstraints
import uuid as UUID
import enum
from fastapi import Form, Query
from core.models.enumrators import Languages


class OrderingResearchInterests(enum.Enum):
    by_title = "title"
    by_most_used = "most_used"
    by_most_used_and_title = "most_used_and_title"


class OnlyUUID(BaseModel):
    uuid: UUID.UUID = Field(...)
    translations: dict[str, dict[str, str]]


class ResearchInterestsOnlyUUID(BaseModel):
    research_interests: List[UUID.UUID]


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


# class TeacherWithResearchInterest(BaseModel):
#     research_interests_viewonly: List[]


class GetResearchInterestsWithTeacher(BaseModel):
    uuid: Annotated[UUID.UUID, Field(serialization_alias="teacher_id")]
    research_interest_viewonly: Annotated[
        List[OnlyUUID], Field(serialization_alias="research_interests")
    ]


class GetResearchInterestsSelectedLanguage(BaseModel):
    title: Optional[str] = None
    uuid: UUID.UUID
    using_count: Optional[int] = None


class GetResearchInterests(GetResearchInterestsSelectedLanguage):
    translations: dict[Languages, dict[str, str]] | None = None


class UpdateResearchInterests(BaseModel):
    translations: (
        Annotated[
            dict[Languages, str],
            Field(
                default=None,
                example={lang.value: {"title": "text"} for lang in Languages},
                description=f"Allowed keys for language: {[lang.value for lang in Languages]}",
            ),
        ]
        | None
    ) = None
    teachers: List[UUID.UUID] | None = None
    pass


class DeleteResearchInterests(BaseModel):
    uuid: UUID.UUID
