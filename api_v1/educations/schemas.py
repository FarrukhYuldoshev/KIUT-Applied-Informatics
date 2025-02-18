from fastapi import Form
from pydantic import BaseModel, Field
from datetime import date
from typing import Optional, List, Annotated
from uuid import UUID
from core.models.enumrators import Roles, Degrees


class GetTeacher(BaseModel):
    uuid: UUID
    full_name: Optional[str] = None
    role: Optional[Roles] = None


class CreateEducation:
    def __init__(
        self,
        place: Annotated[str, Form(max_length=1024)],
        degree: Annotated[Degrees, Form(description="Degree of study")],
        from_date: Annotated[date, Form(description="Starting date of education")],
        to_date: Annotated[date, Form(description="Ending date of education")],
        teacher_id: Annotated[UUID, Form(description="Teacher UUID")],
    ):
        self.place = place
        self.degree = degree
        self.from_date = from_date
        self.to_date = to_date
        self.teacher_id = teacher_id


class GetEducation(BaseModel):
    uuid: UUID
    place: Annotated[str, Field(max_length=1024)]
    degree: Annotated[Degrees, Field(description="Degree of study")]
    from_date: Annotated[date, Field(description="Starting date of education")]
    to_date: Annotated[date, Field(description="Ending date of education")]
    teacher: GetTeacher


class GetEducationWithoutTeacher(BaseModel):
    uuid: UUID
    place: Annotated[str, Field(max_length=1024)]
    degree: Annotated[Degrees, Field(description="Degree of study")]
    from_date: Annotated[date, Field(description="Starting date of education")]
    to_date: Annotated[date, Field(description="Ending date of education")]


class DeleteEducation(BaseModel):
    uuid: UUID


class UpdateEducation(BaseModel):
    place: str | None = None
    degree: Degrees | None = None
    from_date: date | None = None
    to_date: date | None = None
    teacher_id: UUID | None = None
