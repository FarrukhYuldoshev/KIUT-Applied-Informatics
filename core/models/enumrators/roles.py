from enum import Enum


class Roles(Enum):
    HEAD_OF_DEPARTMENT = (
        "Head of the department",
        "Bo‘lim boshlig‘i",
        "Заведующий отделом",
        1,
    )
    PROFESSOR = ("Professor", "Professor", "Профессор", 2)
    ASSOCIATE_PROFESSOR = ("Associate professor", "Dotsent", "Доцент", 3)
    SENIOR_LECTURER = (
        "Senior Lecturer",
        "Katta o‘qituvchi",
        "Старший преподаватель",
        4,
    )
    TEACHER = ("Teacher", "O‘qituvchi", "Преподаватель", 5)
    PROGRAMMER = (
        "Student (Software Engineer)",
        "Talaba (Dasturiy injiniring)",
        "Студент (Программная инженерия)",
        6,
    )

    def __init__(self, en, uz, ru, level):
        self.translations = {"en": en, "uz": uz, "ru": ru}
        self.level = level

    def get_name(self, lang):
        return self.translations.get(lang, self.translations["en"])

    @staticmethod
    def get_position_by_key(key: str):
        return Roles.__members__.get(key, None)  # Agar yo‘q bo‘lsa, None qaytaradi


class RolesForSelect(str, Enum):
    HEAD_OF_DEPARTMENT = "Head of the department"
    PROFESSOR = "Professor"
    ASSOCIATE_PROFESSOR = "Associate professor"
    SENIOR_LECTURER = "Senior Lecturer"
    TEACHER = "Teacher"
    STAFF = "Staff"
