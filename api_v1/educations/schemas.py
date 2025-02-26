from fastapi import Form, Query
from fastapi.params import Depends
from pydantic import BaseModel, Field
from datetime import date
from typing import Optional, List, Annotated, Literal
from uuid import UUID
from core.models.enumrators import Roles, Degrees, Languages
from enum import Enum


class GetTeacher(BaseModel):
    uuid: UUID
    full_name: Optional[str] = None
    role: Optional[Roles] = None


class EducationDetails(BaseModel):
    place: str | None = None
    degree: Degrees | None = None


class CreateEducation:
    def __init__(
        self,
        lang: Annotated[Languages, Query(default=..., alias="lang")],
        place: Annotated[str, Form(max_length=1024, min_length=10)],
        degree: Annotated[
            Degrees,
            Form(
                description="Degree of study",
                min_length=5,
            ),
        ],
        from_date: Annotated[date, Form(description="Starting date of education")],
        to_date: Annotated[date, Form(description="Ending date of education")],
        teacher_id: Annotated[UUID, Form(description="Teacher UUID")],
    ):
        self.lang = lang
        self.place = place
        self.degree = degree
        self.from_date = from_date
        self.to_date = to_date
        self.teacher_id = teacher_id


class GetEducationWithSelectedLanguage(EducationDetails):
    uuid: UUID
    from_date: Annotated[date, Field(description="Starting date of education")]
    to_date: Annotated[date, Field(description="Ending date of education")]
    teacher_id: UUID


class GetEducation(BaseModel):
    uuid: UUID
    from_date: Annotated[date, Field(description="Starting date of education")]
    to_date: Annotated[date, Field(description="Ending date of education")]
    translations: Annotated[dict[Languages, EducationDetails], Field(...)]
    teacher_id: UUID


class GetEducationWithoutTeacher(BaseModel):
    uuid: UUID
    place: Annotated[str, Field(max_length=1024)]
    degree: Annotated[Degrees, Field(description="Degree of study")]
    from_date: Annotated[date, Field(description="Starting date of education")]
    to_date: Annotated[date, Field(description="Ending date of education")]


class UpdateEducation(BaseModel):
    translations: (
        Annotated[
            dict[Languages, EducationDetails],
            Field(
                default=None,
                example={
                    lang.value: {"place": "text", "degree": "text"}
                    for lang in Languages
                },
                description=f"Allowed keys for language: {[lang.value for lang in Languages]}",
            ),
        ]
        | None
    ) = None
    from_date: date | None = None
    to_date: date | None = None
    teacher_id: UUID | None = None
