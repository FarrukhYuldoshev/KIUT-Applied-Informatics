from typing import Annotated, Optional, List, Dict
from pydantic import (
    BaseModel,
    Field,
    StringConstraints,
    model_validator,
    field_validator,
    ConfigDict,
)
import uuid as UUID
import enum
from fastapi import Form, Query
from core.models.enumrators import Languages


class Translations:
    _fields: dict[str, str] = {"title": "text"}


class OnlyUUID(BaseModel):
    uuid: UUID.UUID
    model_config = ConfigDict(from_attributes=True)


class OrderingResearchInterests(enum.Enum):
    by_title = "title"
    by_most_used = "most_used"
    by_most_used_and_title = "most_used_and_title"


class GetResearchInterests(BaseModel):
    uuid: UUID.UUID
    title: str | None = None
    using_count: int = 0
    translations: (
        Annotated[
            dict[str, dict[str, str]],
            Field(
                default=None,
                example={lang.value: {"title": "text"} for lang in Languages},
                description=f"Allowed keys for language: {[lang.value for lang in Languages]}",
            ),
        ]
        | None
    ) = None
    teachers: Annotated[
        List[OnlyUUID],
        Field(default=None, alias="teachers_viewonly", serialization_alias="teachers"),
    ]
    model_config = ConfigDict(from_attributes=True)

    # @model_validator(mode="after")
    # def model_validate(self) -> "GetResearchInterests":
    #     if self.translations is not None:
    #         del self.title
    #     else:
    #         del self.translations
    #     return self


class ResearchInterestsOnlyUUID(BaseModel):
    research_interests: List[UUID.UUID]


class GetTeacherWithResearchInterests(BaseModel):
    uuid: Annotated[UUID.UUID, Field(alias="uuid", serialization_alias="teacher_id")]
    research_interests: Annotated[
        List[GetResearchInterests],
        Field(
            alias="research_interest_viewonly",
            serialization_alias="research_interests",
        ),
    ]


class UpdateResearchInterests(BaseModel, Translations):
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
    teachers: List[UUID.UUID] | None = None

    @field_validator("translations")
    def validate_translations(
        cls, value: Dict[Languages, Dict[str, str]]
    ) -> Dict[Languages, Dict[str, str]]:
        languages = set(lang.value for lang in Languages)
        for lang, data in value.items():
            if not isinstance(lang, Languages):
                raise ValueError(f"Unsupported language expected: {languages}")
            expected_keys = set(Translations._fields.keys())
            data_keys = set(data.keys())
            if extra_keys := data_keys - expected_keys:
                raise ValueError(f"Unexpected keys in translations: {extra_keys}")
            if missing_keys := expected_keys - data_keys:
                raise ValueError(f"Missing keys in translations: {missing_keys}")
        return value


class CreateResearchInterests(UpdateResearchInterests):
    translations: Annotated[
        dict[Languages, dict[str, str]],
        Field(
            default=...,
            example={lang.value: {"title": "text"} for lang in Languages},
            description=f"Allowed keys for language: {[lang.value for lang in Languages]}",
        ),
    ]

    @field_validator("translations")
    def validate_translations(
        cls, value: Dict[Languages, Dict[str, str]]
    ) -> Dict[Languages, Dict[str, str]]:
        languages = set(lang.value for lang in Languages)
        for lang, data in value.items():
            if not isinstance(lang, Languages):
                raise ValueError(f"Unsupported language expected: {languages}")
            languages.remove(lang.value)
            expected_keys = set(Translations._fields.keys())
            data_keys = set(data.keys())
            if extra_keys := data_keys - expected_keys:
                raise ValueError(f"Unexpected keys in translations: {extra_keys}")
            if missing_keys := expected_keys - data_keys:
                raise ValueError(f"Missing keys in translations: {missing_keys}")
        if len(languages) > 0:
            raise ValueError(
                f"Languages not found or duplicate missing {languages} languages"
            )
        return value
