from sqlalchemy import select, ScalarResult, delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload
from core.models import Education, Teachers
from fastapi import HTTPException
from uuid import UUID
from .schemas import (
    CreateEducation,
    UpdateEducation,
)
from starlette import status


async def create_education(session: AsyncSession, data: CreateEducation):
    edu: Education = Education(**data.__dict__)
    stmt = select(Teachers).where(Teachers.uuid == data.teacher_id)
    teacher = await session.scalar(stmt)
    if teacher is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Teacher not found"
        )
    else:
        edu.teacher = teacher
        session.add(edu)
        try:
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
        return edu


async def get_educations_of_teacher(
    session: AsyncSession, teacher_id: UUID
) -> ScalarResult[Education]:
    stmt = select(Education).where(Education.teacher_id == teacher_id)
    educations = await session.scalars(stmt)
    return educations


async def get_education(session: AsyncSession, edu_id: UUID) -> Education:
    stmt = (
        select(Education)
        .where(Education.uuid == edu_id)
        .options(joinedload(Education.teacher))
    )
    edu = await session.scalar(stmt)
    if edu is None:
        raise HTTPException(status_code=404, detail=f"Education not found: {edu_id}")
    else:
        return edu


async def get_all_educations(session: AsyncSession) -> ScalarResult[Education]:
    stmt = select(Education).options(joinedload(Education.teacher))
    educations = await session.scalars(stmt)
    return educations


async def update_education(
    session: AsyncSession, data: UpdateEducation, edu_uuid: UUID, partial=False
):
    edu: Education = await get_education(session=session, edu_id=edu_uuid)
    print(edu)
    for k, v in data.model_dump(exclude_unset=partial).items():
        setattr(edu, k, v)
    try:
        await session.commit()
    except IntegrityError as e:
        if e.orig.__str__().startswith(
            "<class 'asyncpg.exceptions.ForeignKeyViolationError'>"
        ):
            await session.rollback()
            detail = {
                "message": "Teacher not found",
                "details": e.params.__str__(),
            }
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=detail)
        else:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Bad request")
    return edu


async def delete_education(session: AsyncSession, edu_id: UUID):
    edu = await get_education(session=session, edu_id=edu_id)
    stmt = delete(Education).where(Education.uuid == edu.uuid)
    await session.execute(stmt)
    await session.commit()
