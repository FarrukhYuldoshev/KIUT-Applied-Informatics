from typing import Annotated, Optional, List
from pydantic import BaseModel, Field, StringConstraints
import uuid as UUID
import enum
from fastapi import Form, Query
from core.models.enumrators import Languages


class OnlyUUID(BaseModel):
    uuid: UUID.UUID


class OrderingResearchInterests(enum.Enum):
    by_title = "title"
    by_most_used = "most_used"
    by_most_used_and_title = "most_used_and_title"


class GetResearchInterests(BaseModel):
    title: Optional[str] = None
    uuid: UUID.UUID
    using_count: int = 0
    translations: (
        Annotated[
            dict[Languages, dict[str, str]],
            Field(
                default=None,
                example={lang.value: {"title": "text"} for lang in Languages},
                description=f"Allowed keys for language: {[lang.value for lang in Languages]}",
            ),
        ]
        | None
    ) = None


class GetResearchInterestsWithTeacherDetails(GetResearchInterests):
    teachers_viewonly: Annotated[
        List[OnlyUUID],
        Field(
            default=...,
            serialization_alias="teachers",
        ),
    ] = None


class ResearchInterestsOnlyUUID(BaseModel):
    research_interests: List[UUID.UUID]


class CreateResearchInterests:
    def __init__(
        self,
        lang: Annotated[Languages, Query(..., alias="lang")],
        title: Annotated[
            List[Annotated[str, Field(min_length=10)]],
            Form(
                max_length=256,
                description="minimum 10 characters",
            ),
        ] = ["title"],
    ):
        self.title = title
        self.lang = lang


class GetTeacherWithResearchInterests(BaseModel):
    uuid: Annotated[UUID.UUID, Field(serialization_alias="teacher_id")]
    research_interest_viewonly: Annotated[
        List[GetResearchInterests], Field(serialization_alias="research_interests")
    ]


class UpdateResearchInterests(BaseModel):
    translations: (
        Annotated[
            dict[Languages, dict[str, Annotated[str, Field(min_length=10)]]],
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
