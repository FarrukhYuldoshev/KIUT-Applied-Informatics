from enum import Enum


class Degrees(Enum):
    Bsc = (
        "Bachelor's Degree",
        "Бакалавр (Степень бакалавра)",
        "Bakalavr (Bakalavr darajasi)",
        1,
    )
    Msc = (
        "Master of Science",
        "Магистр (Степень магистра)",
        "Magistr (Magistr darajasi)",
        2,
    )
    PhD = (
        "Doctor of Philosophy",
        "Доктор философии",
        "Falsafa doktori",
        3,
    )
    Dsc = (
        "Doctor of Science",
        "Доктор наук",
        "Fan doktori",
        4,
    )

    def __init__(self, en, uz, ru, level):
        self.translations = {"en": en, "uz": uz, "ru": ru}
        self.level = level

    def get_name(self, lang):
        return self.translations.get(lang, self.translations["en"])

    @staticmethod
    def get_position_by_key(key: str):
        for role in Degrees:
            if key in role.translations.values():
                return role
        return None
