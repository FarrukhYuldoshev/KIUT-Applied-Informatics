from typing import Annotated, Optional, Dict, Any, List, ClassVar

from fastapi import Form, File, UploadFile
from pydantic_core.core_schema import ValidationInfo

from core.models.enumrators import Roles, RolesForSelect, Languages
from pydantic import BaseModel, Field, EmailStr, model_validator, ConfigDict
from uuid import UUID as UUID4
from api_v1.educations.schemas import GetEducation
from api_v1.publications.schemas import GetPublicationWithoutTeacher
from api_v1.work_experience.schemas import GetWorkExperience
from api_v1.research_interests.schemas import GetResearchInterests


class OnlyUUID(BaseModel):
    uuid: UUID4 = Field(...)


class CreateTeacher:
    def __init__(
        self,
        full_name_en: Annotated[
            str,
            Form(..., min_length=5, max_length=256, description="Full name in English"),
        ],
        full_name_ru: Annotated[
            str,
            Form(..., min_length=5, max_length=256, description="Full name in Russian"),
        ],
        full_name_uz: Annotated[
            str,
            Form(..., min_length=5, max_length=256, description="Full name in Uzbek"),
        ],
        biography_en: Annotated[
            str,
            Form(..., min_length=20, description="Biography in English"),
        ],
        biography_ru: Annotated[
            str,
            Form(..., min_length=20, description="Biography in Russian"),
        ],
        biography_uz: Annotated[
            str,
            Form(..., min_length=20, description="Biography in Uzbek"),
        ],
        email: Annotated[EmailStr, Form(...)],
        role: Annotated[RolesForSelect, Form(...)],
        image: Annotated[UploadFile, File(description="Teacher's image")],
        scopus_link: Annotated[Optional[str], Form()] = "",
    ):
        self.full_name_en = full_name_en
        self.full_name_ru = full_name_ru
        self.full_name_uz = full_name_uz
        self.biography_en = biography_en
        self.biography_ru = biography_ru
        self.biography_uz = biography_uz
        self.email = email
        self.role = role
        self.image = image
        self.scopus_link = scopus_link


class GetTeachers(BaseModel):
    teacher_id: Annotated[
        UUID4, Field(default=..., alias="uuid", serialization_alias="uuid")
    ]
    full_name: Annotated[str, Field(min_length=5, max_length=256)] = None
    email: Annotated[EmailStr, Field(...)]
    role: Annotated[str, Field()] = None
    scopus_link: Annotated[Optional[str], Field()] = None
    image: Annotated[str, Field(..., description="Teacher's image")]
    translations: Annotated[dict[Languages, dict[str, str]], Field()] = None
    model_config = ConfigDict(from_attributes=True)


class GetTeachersWithResearchInterests(GetTeachers):
    research_interest_viewonly: Annotated[
        List[GetResearchInterests],
        Field(serialization_alias="research_interests"),
    ]
    publications_viewonly: Annotated[
        List["GetPublicationWithoutTeacher"], Field(serialization_alias="publications")
    ]
    work_experiences: Annotated[
        List["GetWorkExperience"],
        Field(serialization_alias="work_experiences"),
    ]
    educations: Annotated[List["GetEducation"], Field(serialization_alias="educations")]
    model_config = ConfigDict(from_attributes=True)


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
