import uuid
from pathlib import Path as Pathlib
import aiofiles
import starlette
from sqlalchemy import (
    select,
    insert,
    ScalarResult,
    update,
    delete,
    case,
    String,
    cast,
    text,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from core.models import Teachers, ResearchInterestsTeacher
from fastapi import HTTPException, UploadFile, Path
from starlette import status
from core.models.enumrators import Roles, Languages
from .schemas import CreateTeacher, UpdateTeacher, GetTeachersWithResearchInterests
from pydantic import EmailStr, ValidationError
from api_v1.educations.crud import get_educations_of_teacher

UPLOAD_DIR = Pathlib("static/files")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


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
    stmt = (
        select(Teachers)
        .where(Teachers.uuid == teacher_id)
        .options(selectinload(Teachers.research_interest_viewonly))
        .options(selectinload(Teachers.publications_viewonly))
        .options(selectinload(Teachers.educations))
        .options(selectinload(Teachers.work_experiences))
    )
    result = await session.scalar(stmt)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Teacher not found"
        )
    else:
        return result


async def create_teacher(session: AsyncSession, data: CreateTeacher) -> Teachers:
    file = await create_file(data.image)
    data.image = file
    role: Roles = Roles.get_position_by_key(data.role.name)
    translations: dict[Languages, dict[str, str]] = {
        Languages.uz: {
            "full_name": data.full_name_uz,
            "role": role.get_name(Languages.uz.value),
            "biography": data.biography_uz,
        },
        Languages.ru: {
            "full_name": data.full_name_ru,
            "role": role.get_name(Languages.ru.value),
            "biography": data.biography_ru,
        },
        Languages.en: {
            "full_name": data.full_name_en,
            "role": role.get_name(Languages.en.value),
            "biography": data.biography_en,
        },
    }
    data_in: dict = {
        "translations": translations,
        "scopus_link": data.scopus_link,
        "email": data.email,
        "image": data.image,
    }
    try:
        teacher: Teachers = await session.scalar(
            insert(Teachers).values(data_in).returning(Teachers)
        )
        await session.commit()
    except IntegrityError as e:
        await session.rollback()
        if Pathlib(data.image).exists():
            Pathlib(data.image).unlink()
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


async def update_teacher(
    teacher_id: uuid.UUID, data: UpdateTeacher, session: AsyncSession
):
    teacher = await get_teacher_or_none(teacher_id=teacher_id, session=session)
    print(data.email)
    if data.email is not None:
        try:
            EmailStr._validate(data.email)
        except Exception:
            raise HTTPException(status_code=422, detail="Invalid email adress")
    if not isinstance(data.image, str) and data.image is not None:
        file = await create_file(data.image)
        data.image = file
        if Pathlib(teacher.image).exists():
            Pathlib(teacher.image).unlink()
    for key, value in data.__dict__.items():
        if value != None and len(value) > 0:
            if key == "image":
                if len(value) == 0:
                    continue
            elif key == "role":
                value = Roles(value)
            print(key, type(value))
            setattr(teacher, key, value)
    await session.commit()
    return teacher


async def delete_teacher(teacher: Teachers, session: AsyncSession):
    stmt = delete(Teachers).where(Teachers.uuid == teacher.uuid)
    await session.execute(stmt)
    await session.commit()


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
