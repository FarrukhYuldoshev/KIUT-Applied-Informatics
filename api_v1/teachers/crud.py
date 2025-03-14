import uuid
from pathlib import Path as Pathlib
from typing import Annotated

import aiofiles
import starlette
from sqlalchemy import (
    select,
    insert,
    ScalarResult,
    delete,
    case,
    update,
    inspect,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from core.models import Teachers, ResearchInterestsTeacher, ResearchInterests
from fastapi import HTTPException, UploadFile, Path, File, Depends
from starlette import status
from core.models.enumrators import Roles, Languages
from core.settings import db_sessions
from .schemas import CreateTeacher, UpdateTeacher, GetTeachersWithResearchInterests
from pydantic import EmailStr, ValidationError
from api_v1.research_interests.crud import get_research_interests_of_teacher
from api_v1.publications.crud import get_publications_of_teacher
from api_v1.work_experience.crud import get_work_experiences_of_teacher
from api_v1.educations.crud import get_education_of_teacher

UPLOAD_DIR = Pathlib("static/files")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


async def set_details_for_teacher(
    teacher: Teachers, session: AsyncSession, lang: Languages = None
) -> GetTeachersWithResearchInterests:
    research_interests = await get_research_interests_of_teacher(
        session=session,
        teacher_id=teacher.uuid,
        lang=lang,
    )
    publications = await get_publications_of_teacher(
        session=session, teacher_id=teacher.uuid
    )
    work_experiences = await get_work_experiences_of_teacher(
        session=session, teacher_id=teacher.uuid, lang=lang
    )
    educations = await get_education_of_teacher(
        teacher_id=teacher.uuid, lang=lang, session=session
    )
    response_model = GetTeachersWithResearchInterests(
        uuid=teacher.uuid,
        email=teacher.email,
        scopus_link=teacher.scopus_link,
        image=teacher.image,
        research_interest_viewonly=research_interests,
        publications_viewonly=publications,
        work_experiences=work_experiences,
        educations=educations,
    )
    if lang is not None:
        response_model.full_name = teacher.translations.get(lang.value, {}).get(
            "full_name"
        )
        response_model.biography = teacher.translations.get(lang.value, {}).get(
            "biography"
        )
        response_model.role = teacher.translations.get(lang.value, {}).get("role")
    else:
        response_model.translations = teacher.translations
    return response_model


async def create_file(file: UploadFile, upload_path=UPLOAD_DIR) -> str:
    try:
        file_extension = file.filename.split(".")[-1]
        content_type = file.content_type
        if content_type.startswith("image/"):
            new_filename = f"{uuid.uuid4()}.{file_extension}"
            file_path = upload_path / new_filename
            print(file_path)
            async with aiofiles.open(file_path, "wb") as buffer:
                await buffer.write(await file.read())
            return str(file_path)
        else:
            raise
    except Exception as e:
        raise HTTPException(
            status_code=starlette.status.HTTP_400_BAD_REQUEST,
            detail="File type not supported",
        )


async def get_teacher_or_none(
    teacher_id: uuid.UUID,
    session: AsyncSession,
):
    stmt = select(Teachers).where(Teachers.uuid == teacher_id)
    result = await session.scalar(stmt)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Teacher not found"
        )
    else:
        return result


async def create_teacher(session: AsyncSession, data: CreateTeacher) -> Teachers:
    try:
        teacher: Teachers = await session.scalar(
            insert(Teachers).values(**data.model_dump()).returning(Teachers)
        )
        await session.commit()
    except IntegrityError as e:
        await session.rollback()
        if e.orig.__str__().startswith(
            "<class 'asyncpg.exceptions.UniqueViolationError'>"
        ):
            detail = {
                "code": "unique_violation",
                "message": "The values already exist",
                "details": e.params.__str__(),
            }
            raise HTTPException(status.HTTP_409_CONFLICT, detail=detail)
        else:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Database error")
    return teacher


async def set_image(
    image: Annotated[UploadFile, File(...)],
    teacher_id: Annotated[uuid.UUID, Path(alias="uuid")],
    session: AsyncSession = Depends(db_sessions.session_dependency),
):
    stmt = select(Teachers.uuid).where(Teachers.uuid == teacher_id)
    result = await session.scalar(stmt)
    if result is not None:
        file = await create_file(image, UPLOAD_DIR)
        stmt = (
            update(Teachers)
            .where(Teachers.uuid == teacher_id)
            .values(image=file)
            .returning(Teachers)
        )
        try:
            result = await session.scalar(stmt)
            await session.commit()
        except IntegrityError as e:
            await session.rollback()
            if Pathlib(file).exists():
                Pathlib(file).unlink()
        return result
    else:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Teacher not found")


async def update_teacher(
    teacher_id: uuid.UUID, data: UpdateTeacher, session: AsyncSession
):
    teacher = await get_teacher_or_none(teacher_id=teacher_id, session=session)
    for key, value in data.model_dump(exclude_unset=True).items():
        if key == "translations":
            teacher.translations.update(**data.translations)
        else:
            setattr(teacher, key, value)
    try:
        await session.commit()
    except IntegrityError as e:
        if "UniqueViolationError" in str(e.orig):
            raise HTTPException(
                status_code=409,
                detail=f"Teacher email conflict:  {e}",
            )
        raise HTTPException(status_code=400, detail="Bad request")
    return teacher


async def delete_teacher(teacher: Teachers, session: AsyncSession):
    stmt = delete(Teachers).where(Teachers.uuid == teacher.uuid)
    await session.execute(stmt)
    await session.commit()
    if Pathlib(teacher.image).exists() and teacher.image != "static/default.png":
        Pathlib(teacher.image).unlink()


async def get_all_teachers(session: AsyncSession) -> ScalarResult[Teachers]:
    role_level_order = case(
        (
            Teachers.translations["en"]["role"].astext
            == Roles.HEAD_OF_DEPARTMENT.get_name("en"),
            Roles.HEAD_OF_DEPARTMENT.level,
        ),
        (
            Teachers.translations["en"]["role"].astext
            == Roles.PROFESSOR.get_name("en"),
            Roles.PROFESSOR.level,
        ),
        (
            Teachers.translations["en"]["role"].astext
            == Roles.ASSOCIATE_PROFESSOR.get_name("en"),
            Roles.ASSOCIATE_PROFESSOR.level,
        ),
        (
            Teachers.translations["en"]["role"].astext
            == Roles.SENIOR_LECTURER.get_name("en"),
            Roles.SENIOR_LECTURER.level,
        ),
        (
            Teachers.translations["en"]["role"].astext == Roles.TEACHER.get_name("en"),
            Roles.TEACHER.level,
        ),
        (
            Teachers.translations["en"]["role"].astext
            == Roles.PROGRAMMER.get_name("en"),
            Roles.PROGRAMMER.level,
        ),
    )

    stmt = select(Teachers).order_by(role_level_order.asc())
    result = await session.scalars(stmt)
    return result
