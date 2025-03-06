from typing import Dict, Annotated

from pydantic import BaseModel, Field, field_validator

from core.models.enumrators import Languages
from uuid import UUID as uuid4


class Translations:
    _fields: Dict[str, str] = {
        "name": "name of subject",
        "description": "description of subject",
    }


class CreateSubject(BaseModel, Translations):
    translations: Annotated[
        Dict[Languages, Dict[str, str]],
        Field(
            ...,
            example={lang.value: {**Translations._fields} for lang in Languages},
            description=f"Allowed keys for language{[lang.value for lang in Languages]}",
        ),
    ]
    credits: Annotated[int, Field(..., gt=0)]
    semester: Annotated[int, Field(..., gt=0)]
    academic_program_id: Annotated[uuid4, Field(...)]

    @field_validator("translations")
    def validate_translations(
        cls, value: Dict[Languages, Dict[str, str]]
    ) -> Dict[Languages, Dict[str, str]]:
        languages = [lang.value for lang in Languages]
        langs: set[str] = set(languages)
        for lang, data in value.items():
            if not isinstance(lang, Languages):
                raise ValueError(f"Unsupported language expected: {languages}")
            langs.remove(lang.value)
            supported_keys = set(Translations._fields.keys())
            data_keys = set(data.keys())
            extra_keys = data_keys - supported_keys
            if extra_keys:
                raise ValueError(
                    f"Unexpected keys in translations {extra_keys} where '{lang.value}': {data}"
                )
            missing_keys = supported_keys - data_keys
            if missing_keys:
                raise ValueError(
                    f"Missing keys in translations {missing_keys} where '{lang.value}': {data}"
                )
        if len(langs) > 0:
            raise ValueError(f"Missing language:  {langs}")
        return value
