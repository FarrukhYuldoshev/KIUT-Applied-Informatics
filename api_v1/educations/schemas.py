from fastapi import Form, Query
from pydantic import BaseModel, Field, field_validator, ConfigDict
from datetime import date
from typing import Annotated, Dict
from uuid import UUID
from core.models.enumrators import Languages, Degrees


class Translation:
    fields: Dict[str, str] = {"place": "text", "degree": "text"}


class CreateEducation(BaseModel):
    translations: Annotated[
        Dict[Languages, dict[str, str]],
        Field(
            ...,
            example={
                lang.value: {"place": "text", "degree": "text"} for lang in Languages
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
        supporting_degrees = set()
        current_degree = None
        for degree in Degrees:
            for lang in Languages:
                supporting_degrees.add(degree.translations[lang])
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
                    raise ValueError("Minimum length for place field is 10 characters!")
            if data["degree"] not in supporting_degrees:
                raise ValueError(
                    f"Unexpected degree in translation supporting degrees: {supporting_degrees}"
                )
            else:
                if current_degree is None:
                    current_degree = Degrees.get_position_by_key(data["degree"])
                else:
                    if current_degree != Degrees.get_position_by_key(data["degree"]):
                        raise ValueError(
                            "Not matching degree with several translations"
                        )

        if len(supporting_languages) > 0:
            raise ValueError(
                f"Missing languages in translations {supporting_languages}"
            )
        return value


class GetEducation(BaseModel):
    uuid: UUID
    place: str | None = None
    degree: str | None = None
    from_date: Annotated[date, Field(description="Starting date of education")]
    to_date: Annotated[date, Field(description="Ending date of education")]
    translations: Annotated[dict[Languages, dict[str, str]], Field()] = None
    teacher_id: UUID | None = None
    model_config = ConfigDict(from_attributes=True)


class UpdateEducation(CreateEducation):
    translations: (
        Annotated[
            dict[Languages, dict[str, str]],
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

    @field_validator("translations")
    def validate_translations(
        cls, value: Dict[Languages, Dict[str, str]]
    ) -> Dict[Languages, Dict[str, str]]:
        supporting_degrees = set()
        current_degree = None
        for degree in Degrees:
            for lang in Languages:
                supporting_degrees.add(degree.translations[lang])
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
            if (
                data.get("degree", None) is not None
                and data["degree"] not in supporting_degrees
            ):
                raise ValueError(
                    f"Unexpected degree in translation supporting degrees: {supporting_degrees}"
                )
            elif data.get("degree") is not None:
                if current_degree is None:
                    current_degree = Degrees.get_position_by_key(data["degree"])
                else:
                    if current_degree != Degrees.get_position_by_key(data["degree"]):
                        raise ValueError(
                            "Not matching degree with several translations"
                        )
        return value

    from_date: date | None = None
    to_date: date | None = None
    teacher_id: UUID | None = None
