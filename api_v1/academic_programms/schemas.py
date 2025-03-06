from typing import Annotated, Any, List, Dict, ClassVar

from pydantic import BaseModel, Field, field_validator

from core.models.enumrators import Languages, StudyFormat

from uuid import UUID as UUID4


class Translations:
    _fields: Dict[str, str] = {
        "title": "text",
        "program": "text",
        "study_format": [],
    }


class OnlyUUID(BaseModel):
    uuid: UUID4


class GetAcademicPrograms(BaseModel):
    uuid: UUID4
    translations: Annotated[Dict[Languages, Dict[str, List[str] | str]], Field()] = None
    title: Annotated[str, Field(max_length=256)] = None
    program: Annotated[str, Field(max_length=256)] = None
    study_format: Annotated[list[str], Field(max_length=256)] = None
    year_of_study: Annotated[int, Field(ge=1)]


class GetAcademicProgramsWithSubjects(GetAcademicPrograms):
    subjects: Annotated[list[OnlyUUID], Field(default=None)]


class CreateAcademicProgram(BaseModel, Translations):
    translations: Annotated[
        Dict[Languages, Dict[str, List[str] | str]],  # study_format = list[str]
        Field(
            example={lang.value: {**Translations._fields} for lang in Languages},
            description=f"Allowed keys for language: {[lang.value for lang in Languages]}",
        ),
    ]
    year_of_study: Annotated[int, Field(ge=1, description="The year of the study")]

    @field_validator("translations")
    def validate_translations(
        cls, value: Dict[Languages, Dict[str, str | List[str]]]
    ) -> Dict[Languages, Dict[str, str | List[str]]]:
        allowed_keys = set(Translations._fields.keys())
        allowed_study_formats = set()
        for sf in StudyFormat:
            for x in sf.value:
                allowed_study_formats.add(x)
        languages = set()
        languages.update(["uz", "ru", "en"])
        for lang, data in value.items():
            if not isinstance(lang, Languages):
                raise ValueError(
                    f"Invalid language: {lang}. Allowed: {[l.value for l in Languages]}"
                )
            languages.remove(lang)
            data_keys = set(data.keys())
            extra_keys = data_keys - allowed_keys
            missing_keys = allowed_keys - data_keys
            if extra_keys or missing_keys:
                if extra_keys:
                    raise ValueError(
                        f"Invalid keys {extra_keys} in translations. Allowed keys: {allowed_keys}"
                    )
                else:
                    raise ValueError(
                        f"Missing keys {missing_keys} in translations. Allowed keys: {allowed_keys}"
                    )

            if "study_format" in data:
                study_formats = data["study_format"]
                if not isinstance(study_formats, list) or len(study_formats) < 1:
                    raise ValueError(
                        f"'study_format' must be a list of strings and must include one element"
                    )

                invalid_values = [
                    sf for sf in study_formats if sf not in allowed_study_formats
                ]
                if invalid_values:
                    raise ValueError(
                        f"Invalid study_format values: {invalid_values}. Allowed: {list(allowed_study_formats)}"
                    )
        if len(languages) >= 1:
            raise ValueError("Not enough languages missing: ", languages)
        return value

    #                 )
