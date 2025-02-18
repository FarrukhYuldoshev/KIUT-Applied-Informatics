from sqlalchemy import select, ScalarResult, delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload
from core.models import Teachers, WorkExperience
from fastapi import HTTPException
from uuid import UUID
from .schemas import (
    CreateWorkExperience,
    UpdateWorkExperience,
)
from starlette import status


async def create_work_experience(session: AsyncSession, data: CreateWorkExperience):
    work: WorkExperience = WorkExperience(**data.__dict__)
    stmt = select(Teachers).where(Teachers.uuid == data.teacher_id)
    teacher = await session.scalar(stmt)
    if teacher is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Teacher not found"
        )
    else:
        work.teacher = teacher
        session.add(work)
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
        return work


async def get_work_experience_of_teacher(
    session: AsyncSession, teacher_id: UUID
) -> ScalarResult[WorkExperience]:
    stmt = select(WorkExperience).where(WorkExperience.teacher_id == teacher_id)
    work_experiences = await session.scalars(stmt)
    return work_experiences


async def get_work_experience(
    session: AsyncSession, work_experience_id: UUID
) -> WorkExperience:
    stmt = (
        select(WorkExperience)
        .where(WorkExperience.uuid == work_experience_id)
        .options(joinedload(WorkExperience.teacher))
    )
    work = await session.scalar(stmt)
    if work is None:
        raise HTTPException(
            status_code=404, detail=f"Education not found: {work_experience_id}"
        )
    else:
        return work


async def get_all_work_experience(
    session: AsyncSession,
) -> ScalarResult[WorkExperience]:
    stmt = select(WorkExperience).options(joinedload(WorkExperience.teacher))
    work_experiences = await session.scalars(stmt)
    return work_experiences


async def update_education(
    session: AsyncSession,
    data: UpdateWorkExperience,
    work_experience_id: UUID,
    partial=False,
):
    work: WorkExperience = await get_work_experience(
        session=session, work_experience_id=work_experience_id
    )
    for k, v in data.model_dump(exclude_unset=partial).items():
        setattr(work, k, v)
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
    return work


async def delete_work_experience(session: AsyncSession, work_experience_id: UUID):
    work = await get_work_experience(
        session=session, work_experience_id=work_experience_id
    )
    stmt = delete(WorkExperience).where(WorkExperience.uuid == work.uuid)
    await session.execute(stmt)
    await session.commit()
