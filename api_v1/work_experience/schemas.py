from fastapi import Form, Query
from pydantic import BaseModel, Field
from datetime import date
from typing import Annotated
from uuid import UUID
from core.models.enumrators import Languages


class WorkExperienceDetails(BaseModel):
    place: str | None = None
    role: str | None = None


class CreateWorkExperience:
    def __init__(
        self,
        lang: Annotated[Languages, Query(default=..., alias="lang")],
        place: Annotated[str, Form(max_length=1024, min_length=10)],
        role: Annotated[
            str,
            Form(
                description="The role",
                min_length=4,
            ),
        ],
        from_date: Annotated[date, Form(description="Starting date of education")],
        to_date: Annotated[date, Form(description="Ending date of education")],
        teacher_id: Annotated[UUID, Form(description="Teacher UUID")],
    ):
        self.lang = lang
        self.place = place
        self.role = role
        self.from_date = from_date
        self.to_date = to_date
        self.teacher_id = teacher_id


class GetWorkExperienceWithSelectedLanguage(WorkExperienceDetails):
    uuid: UUID
    from_date: Annotated[date, Field(description="Starting date of education")]
    to_date: Annotated[date, Field(description="Ending date of education")]
    teacher_id: UUID


class GetWorkExperience(BaseModel):
    uuid: UUID
    from_date: Annotated[date, Field(description="Starting date of education")]
    to_date: Annotated[date, Field(description="Ending date of education")]
    translations: Annotated[dict[Languages, WorkExperienceDetails], Field(...)]
    teacher_id: UUID


class UpdateWorkExperience(BaseModel):
    translations: (
        Annotated[
            dict[Languages, WorkExperienceDetails],
            Field(
                default=None,
                example={
                    lang.value: {"place": "text", "role": "text"}
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
