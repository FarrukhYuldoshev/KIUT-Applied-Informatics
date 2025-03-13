from sqladmin import ModelView
from core.models import *
from wtforms import TextAreaField
import json


class TeachersView(ModelView, model=Teachers):
    name = "Teacher"
    name_plural = "Teachers"
    icon = "fa-solid fa-users"
    category = "Teachers information"
    column_searchable_list = [Teachers.translations]
    column_list = [
        Teachers.uuid,
        "full_name",
        Teachers.email,
        Teachers.scopus_link,
    ]
    column_formatters = {
        "full_name": lambda m, a: (
            m.translations["en"].get("full_name") if m.translations else None
        ),
        "translations": lambda m, a: json.dumps(
            m.jsonb_field, indent=4, ensure_ascii=False
        ),
    }
    form_columns = [
        Teachers.email,
        Teachers.scopus_link,
        Teachers.translations,
        Teachers.publications_viewonly,
        Teachers.research_interest_viewonly,
    ]


class ResearchInterestsView(ModelView, model=ResearchInterests):
    name = "ResearchInterest"
    name_plural = "ResearchInterests"
    icon = "fa-solid fa-book"
    category = "Teachers information"
    column_searchable_list = [ResearchInterests.translations]
    column_list = [
        ResearchInterests.uuid,
        "title",
    ]
    column_formatters = {
        "title": lambda m, a: (
            m.translations.get("en", {}).get("title") if m.translations else None
        ),
        "translations": lambda m, a: json.dumps(
            m.jsonb_field, indent=4, ensure_ascii=False
        ),
    }
    form_columns = [ResearchInterests.translations, ResearchInterests.teachers_viewonly]
    # form_overrides = {
    #     "research_interest": SelectMultipleField,
    # }


class PublicationsView(ModelView, model=Publications):
    name = "Publication"
    name_plural = "Publications"
    icon = "fa-solid fa-book-open"
    category = "Teachers information"
    column_searchable_list = [Publications.title]
    column_list = [
        Publications.uuid,
        Publications.title,
    ]
    form_columns = [
        Publications.title,
        Publications.pre_print_link,
        Publications.link,
        Publications.teachers_viewonly,
    ]


class EducationView(ModelView, model=Education):
    name = "Education"
    name_plural = "Educations"
    icon = "fa-solid fa-graduation-cap"
    category = "Teachers information"
    column_searchable_list = [Education.translations]
    column_list = [
        Education.uuid,
        "place",
        "degree",
        Education.from_date,
        Education.to_date,
        Education.teacher_id,
    ]
    column_formatters = {
        "place": lambda m, a: (
            m.translations.get("en", {}).get("place") if m.translations else None
        ),
        "degree": lambda m, a: (
            m.translations.get("en", {}).get("degree") if m.translations else None
        ),
        "translations": lambda m, a: json.dumps(
            m.jsonb_field, indent=4, ensure_ascii=False
        ),
    }


class SubjectsView(ModelView, model=Subjects):
    name = "Subject"
    name_plural = "Subjects"
    icon = "fa-solid fa-swatchbook"
    category = "Academic information"
    column_searchable_list = [Subjects.translations]
    column_list = [
        Subjects.uuid,
        "name",
        "description",
        Subjects.credits,
        Subjects.semester,
        Subjects.academic_program,
    ]
    column_formatters = {
        "name": lambda m, a: (
            m.translations.get("en", {}).get("name") if m.translations else None
        ),
        "description": lambda m, a: (
            m.translations.get("en", {}).get("description") if m.translations else None
        ),
        "translations": lambda m, a: json.dumps(
            m.jsonb_field, indent=4, ensure_ascii=False
        ),
    }


class AcademicProgramsView(ModelView, model=AcademicPrograms):
    name = "Academic Program"
    name_plural = "Academic Programs"
    icon = "fa-solid fa-marker"
    category = "Academic information"
    column_searchable_list = [AcademicPrograms.translations]
    column_list = [
        AcademicPrograms.uuid,
        "title",
        "program",
        "study_format",
        AcademicPrograms.year_of_study,
    ]
    column_formatters = {
        "title": lambda m, a: (
            m.translations.get("en", {}).get("title") if m.translations else None
        ),
        "program": lambda m, a: (
            m.translations.get("en", {}).get("program") if m.translations else None
        ),
        "study_format": lambda m, a: (
            m.translations.get("en", {}).get("study_format") if m.translations else None
        ),
        "translations": lambda m, a: json.dumps(
            m.jsonb_field, indent=4, ensure_ascii=False
        ),
    }
