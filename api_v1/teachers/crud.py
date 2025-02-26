import uuid
from pathlib import Path as Pathlib
from typing import Annotated

import aiofiles
import starlette
from sqlalchemy import select, insert, ScalarResult, update, delete, case
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from core.models import Teachers, ResearchInterestsTeacher
from fastapi import HTTPException, UploadFile, Path
from starlette import status
from core.models.enumrators import Roles, RolesRate
from .schemas import CreateTeacher, UpdateTeacher
from pydantic import EmailStr, ValidationError

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
    try:
        teacher: Teachers = await session.scalar(
            insert(Teachers).values(data.__dict__).returning(Teachers)
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
            Teachers.role == Roles.head_of_the_department,
            RolesRate.head_of_the_department.value,
        ),
        (
            Teachers.role == Roles.professor,
            RolesRate.professor.value,
        ),
        (
            Teachers.role == Roles.associate_professor,
            RolesRate.associate_professor.value,
        ),
        (Teachers.role == Roles.senior_lecturer, RolesRate.senior_lecturer.value),
        (Teachers.role == Roles.teacher, RolesRate.teacher.value),
        (Teachers.role == Roles.staff, RolesRate.staff.value),
    )
    stmt = (
        select(Teachers)
        .options(selectinload(Teachers.research_interest_viewonly))
        .options(selectinload(Teachers.publications_viewonly))
        .options(selectinload(Teachers.educations))
        .options(selectinload(Teachers.work_experiences))
        .order_by(role_level_order)
    )
    result = await session.scalars(stmt)
    return result
