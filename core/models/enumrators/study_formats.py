from enum import Enum


class StudyFormat(Enum):
    FULL_TIME = (
        "Full-time study",
        "Kunduzgi ta’lim",
        "Очное обучение",
    )
    PART_TIME = (
        "Part-time study",
        "Kechki ta’lim",
        "Вечернее обучение",
    )
    DISTANCE_LEARNING = (
        "Distance learning",
        "Masofaviy ta’lim",
        "Дистанционное обучение",
    )

    EXTRAMURAL_STUDY = (
        "Extramural studies",
        "Sirtqi ta’lim",
        "Заочное обучение",
    )

    def __init__(self, en, uz, ru):
        self.translations = {"en": en, "uz": uz, "ru": ru}

    def get_name(self, lang):
        return self.translations.get(lang, self.translations["en"])

    @staticmethod
    def get_position_by_key(key: str):
        return StudyFormat.__members__.get(key, None)
