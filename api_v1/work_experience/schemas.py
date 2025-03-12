from fastapi import Form, Query
from pydantic import BaseModel, Field, field_validator, ConfigDict
from datetime import date
from typing import Annotated, Dict
from uuid import UUID
from core.models.enumrators import Languages


class Translation:
    fields: Dict[str, str] = {"place": "text", "role": "text"}


class CreateWorkExperience(BaseModel):
    translations: Annotated[
        Dict[Languages, dict[str, str]],
        Field(
            ...,
            example={
                lang.value: {"place": "text", "role": "text"} for lang in Languages
            },
        ),
    ]
    from_date: Annotated[date, Field(description="Starting date of education")]
    to_date: Annotated[date, Field(description="Ending date of education")]
    teacher_id: Annotated[UUID, Field(description="Teacher UUID")]

    @field_validator("translations")
    def validate_translations(
        cls, value: Dict[Languages, Dict[str, str]]
    ) -> Dict[Languages, Dict[str, str]]:
        supporting_languages = set([lang.value for lang in Languages])
        for lang, data in value.items():
            if not isinstance(lang, Languages):
                raise ValueError(f"Unsupported language: {lang}")
            supporting_languages.remove(lang.value)
            expected_keys = set(Translation.fields.keys())
            data_keys = set(data.keys())
            if missing_keys := expected_keys - data_keys:
                raise ValueError(f"Missing keys in translations: {missing_keys}")
            if extra_keys := data_keys - expected_keys:
                raise ValueError(f"Extra keys in translations: {extra_keys}")
            for key, val in data.items():
                if len(val) < 10 and key == "place":
                    ValueError("Minimum length for place field is 10 characters!")
                elif len(val) < 4 and key == "role":
                    ValueError("Minimum length for role field is 4 characters!")
        if len(supporting_languages) > 0:
            raise ValueError(
                f"Missing languages in translations {supporting_languages}"
            )
        return value


class GetWorkExperience(BaseModel):
    uuid: UUID
    place: str | None = None
    role: str | None = None
    from_date: Annotated[date, Field(description="Starting date of education")]
    to_date: Annotated[date, Field(description="Ending date of education")]
    translations: Annotated[dict[Languages, dict[str, str]], Field()] = None
    teacher_id: UUID | None = None
    model_config = ConfigDict(from_attributes=True)


class UpdateWorkExperience(CreateWorkExperience):
    translations: (
        Annotated[
            dict[Languages, dict[str, str]],
            Field(
                default=None,
                example={
                    lang.value: {"place": "text", "role": "text"} for lang in Languages
                },
                description=f"Allowed keys for language: {[lang.value for lang in Languages]}",
            ),
        ]
        | None
    ) = None

    @field_validator("translations")
    def validate_translations(
        cls, value: Dict[Languages, Dict[str, str]]
    ) -> Dict[Languages, Dict[str, str]]:
        for lang, data in value.items():
            if not isinstance(lang, Languages):
                raise ValueError(f"Unsupported language: {lang}")
            expected_keys = set(Translation.fields.keys())
            data_keys = set(data.keys())
            if missing_keys := expected_keys - data_keys:
                raise ValueError(f"Missing keys in translations: {missing_keys}")
            if extra_keys := data_keys - expected_keys:
                raise ValueError(f"Extra keys in translations: {extra_keys}")
            for key, val in data.items():
                if len(val) < 10 and key == "place":
                    raise ValueError("Minimum length for place field is 10 characters!")
                elif len(val) < 4 and key == "role":
                    raise ValueError("Minimum length for role field is 4 characters!")
        return value

    from_date: date | None = None
    to_date: date | None = None
    teacher_id: UUID | None = None
