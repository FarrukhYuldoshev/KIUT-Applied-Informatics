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


class CreateWorkExperience:
    def __init__(
        self,
        place: Annotated[str, Form(max_length=1024)],
        role: Annotated[str, Form(max_length=256, description="Role in your company")],
        from_date: Annotated[date, Form(description="Starting date of job")],
        to_date: Annotated[date, Form(description="Ending date of job")],
        teacher_id: Annotated[UUID, Form(description="Teacher UUID")],
    ):
        self.place = place
        self.role = role
        self.from_date = from_date
        self.to_date = to_date
        self.teacher_id = teacher_id


class GetWorkExperience(BaseModel):
    uuid: UUID
    place: str
    role: str
    from_date: date
    to_date: date
    teacher: GetTeacher


class GetWorkExperienceWithoutTeacher(BaseModel):
    uuid: UUID
    place: str
    role: str
    from_date: date
    to_date: date


class DeleteWorkExperience(BaseModel):
    uuid: UUID


class UpdateWorkExperience(BaseModel):
    place: str | None = None
    role: str | None = None
    from_date: date | None = None
    to_date: date | None = None
    teacher_id: UUID | None = None
