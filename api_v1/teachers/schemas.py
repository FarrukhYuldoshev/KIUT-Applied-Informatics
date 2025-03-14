from typing import Annotated, Optional, Dict, Any, List, ClassVar

from fastapi import Form, File, UploadFile
from pydantic_core.core_schema import ValidationInfo

from core.models.enumrators import Roles, Languages
from pydantic import (
    BaseModel,
    Field,
    EmailStr,
    ConfigDict,
    field_validator,
)
from uuid import UUID as UUID4
from api_v1.educations.schemas import GetEducation
from api_v1.publications.schemas import GetPublication
from api_v1.work_experience.schemas import GetWorkExperience
from api_v1.research_interests.schemas import GetResearchInterests


class OnlyUUID(BaseModel):
    uuid: UUID4 = Field(...)


class Translations:
    fields: Dict[str, str] = {
        "full_name": "text",
        "biography": "text",
        "role": "text",
    }


class CreateTeacher(BaseModel):
    email: Annotated[EmailStr, Field(...)]
    scopus_link: Annotated[str, Field(None, min_length=1)]
    translations: Annotated[
        Dict[Languages, Dict[str, str]],
        Field(..., example={lang.value: Translations.fields for lang in Languages}),
    ]
    image: Annotated[str, Field(default="static/default.png")]

    @field_validator("translations")
    def validate_translations(
        cls, value: Dict[Languages, Dict[str, str]]
    ) -> Dict[Languages, Dict[str, str]]:
        supporting_languages = set(lang.value for lang in Languages)
        expected_keys = set(Translations.fields.keys())
        roles_uz = [role.translations["uz"] for role in Roles]
        roles_ru = [role.translations["ru"] for role in Roles]
        roles_en = [role.translations["en"] for role in Roles]
        current_role = None
        for lang, data in value.items():
            if not isinstance(lang, Languages):
                raise ValueError(f"Supporting languages only {supporting_languages}")
            supporting_languages.remove(lang.value)
            data_keys = set(data.keys())
            if extra_keys := data_keys - expected_keys:
                raise ValueError(f"Unexpected keys in translations: {extra_keys}")
            if missing_keys := expected_keys - data_keys:
                raise ValueError(f"Missing keys in translations: {missing_keys}")
            if lang == Languages.en:
                if data["role"] not in roles_en:
                    raise ValueError(
                        f"Unexpected role in english translations: {data['role']} Expected: {roles_en}"
                    )
            elif lang == Languages.ru:
                if data["role"] not in roles_ru:
                    raise ValueError(
                        f"Unexpected role in russian translations: {data['role']} Expected: {roles_ru}"
                    )
            else:
                if data["role"] not in roles_uz:
                    raise ValueError(
                        f"Unexpected role in uzbek translations: {data['role']} Expected: {roles_uz}"
                    )

            if current_role is None:
                current_role = Roles.get_position_by_key(data["role"])
            elif current_role is not None and current_role != Roles.get_position_by_key(
                data["role"]
            ):
                raise ValueError("Roles not matching!")
        if len(supporting_languages) > 0:
            raise ValueError(f"Missing languages:  {supporting_languages}")
        return value


class UploadImage:
    def __init__(
        self, image: Annotated[UploadFile, File(description="Teacher's image")]
    ):
        self.image = image


class GetTeachers(BaseModel):
    teacher_id: Annotated[
        UUID4, Field(default=..., alias="uuid", serialization_alias="uuid")
    ]
    full_name: Annotated[str, Field(max_length=256)] = None
    email: Annotated[EmailStr, Field(...)]
    role: Annotated[str, Field()] | None = None
    biography: Annotated[str, Field()] | None = None
    scopus_link: Annotated[Optional[str], Field()] = None
    image: Annotated[str, Field(..., description="Teacher's image")]
    translations: Annotated[dict[Languages, dict[str, str]], Field()] = None
    model_config = ConfigDict(from_attributes=True)


class GetTeachersWithResearchInterests(GetTeachers):
    research_interest_viewonly: Annotated[
        List[GetResearchInterests],
        Field(
            serialization_alias="research_interests", alias="research_interest_viewonly"
        ),
    ]
    publications_viewonly: Annotated[
        List["GetPublication"], Field(serialization_alias="publications")
    ]
    work_experiences: Annotated[
        List["GetWorkExperience"],
        Field(serialization_alias="work_experiences"),
    ]
    educations: Annotated[List["GetEducation"], Field(serialization_alias="educations")]
    model_config = ConfigDict(from_attributes=True)


class UpdateTeacher(CreateTeacher):
    email: Annotated[EmailStr, Field(None)]
    scopus_link: Annotated[str, Field(None, min_length=1)]
    translations: Annotated[
        Dict[Languages, Dict[str, str]],
        Field(None, example={lang.value: Translations.fields for lang in Languages}),
    ]
    image: Annotated[str, Field("static/default.png", exclude=True)]

    @field_validator("translations")
    def validate_translations(
        cls, value: Dict[Languages, Dict[str, str]]
    ) -> Dict[Languages, Dict[str, str]]:
        expected_keys = set(Translations.fields.keys())
        roles_uz = [role.translations["uz"] for role in Roles]
        roles_ru = [role.translations["ru"] for role in Roles]
        roles_en = [role.translations["en"] for role in Roles]
        current_role = None
        for lang, data in value.items():
            if not isinstance(lang, Languages):
                raise ValueError(f"Unexpected language: {lang}")
            data_keys = set(data.keys())
            if extra_keys := data_keys - expected_keys:
                raise ValueError(f"Unexpected keys in translations: {extra_keys}")
            if data.get("role", None) is not None:
                if lang == Languages.en:
                    if data["role"] not in roles_en:
                        raise ValueError(
                            f"Unexpected role in english translations: {data['role']} Expected: {roles_en}"
                        )
                elif lang == Languages.ru:
                    if data["role"] not in roles_ru:
                        raise ValueError(
                            f"Unexpected role in russian translations: {data['role']} Expected: {roles_ru}"
                        )
                else:
                    if data["role"] not in roles_uz:
                        raise ValueError(
                            f"Unexpected role in uzbek translations: {data['role']} Expected: {roles_uz}"
                        )
                role_temp = Roles.get_position_by_key(data["role"])
                if current_role is None:
                    current_role = role_temp
                elif (
                    current_role is not None
                    and role_temp is not None
                    and current_role != role_temp
                ):
                    raise ValueError("Roles not matching!")
        return value
