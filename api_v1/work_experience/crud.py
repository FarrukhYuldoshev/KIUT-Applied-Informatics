from typing import Annotated
from fastapi.params import Query
from sqlalchemy import select, delete, insert, Row, Sequence, update
from sqlalchemy.ext.asyncio import AsyncSession
from core.models import WorkExperience, Teachers
from core.settings import db_sessions
from fastapi import HTTPException, Depends, Path
from uuid import UUID

from core.models.enumrators import Languages
from .schemas import (
    CreateWorkExperience,
    UpdateWorkExperience,
    GetWorkExperience,
)
from starlette import status


def convert_sql_model_to_base_model(
    work_experience: WorkExperience, lang: Languages = None
) -> GetWorkExperience:
    response_model = GetWorkExperience(
        uuid=work_experience.uuid,
        from_date=work_experience.from_date,
        to_date=work_experience.to_date,
        teacher_id=work_experience.teacher_id,
    )
    if lang is not None:
        response_model.place = work_experience.translations.get(lang, {}).get("place")
        response_model.role = work_experience.translations.get(lang, {}).get("role")
    else:
        response_model.translations = work_experience.translations
    return response_model


async def get_work_experiences_of_teacher(
    session: AsyncSession, teacher_id: UUID, lang: Languages = None
) -> list[GetWorkExperience]:
    stmt = (
        select(WorkExperience)
        .where(WorkExperience.teacher_id == teacher_id)
        .order_by(WorkExperience.from_date.desc(), WorkExperience.to_date.desc())
    )
    result = await session.scalars(stmt)
    return [convert_sql_model_to_base_model(obj, lang=lang) for obj in result]


async def create_work_experience(session: AsyncSession, data: CreateWorkExperience):
    stmt = select(Teachers.uuid).where(Teachers.uuid == data.teacher_id)
    teacher_id = await session.scalar(stmt)
    if teacher_id is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Teacher not found"
        )
    else:
        stmt = (
            insert(WorkExperience).values(**data.model_dump()).returning(WorkExperience)
        )
        result = await session.scalar(stmt)
        await session.commit()
        return result


async def get_work_experience(
    work_experience_id: Annotated[UUID, Path(alias="work_experience_id")],
    session: AsyncSession = Depends(db_sessions.session_dependency),
) -> WorkExperience:

    stmt = select(WorkExperience).where(WorkExperience.uuid == work_experience_id)
    result = await session.scalar(stmt)
    if result is None:
        raise HTTPException(status_code=404, detail="Work experience not found")
    else:
        return result


async def get_all_work_experiences(session: AsyncSession):
    stmt = select(WorkExperience)
    result = await session.scalars(stmt)
    return result


async def update_work_experience(
    session: AsyncSession, data: UpdateWorkExperience, work_experience: Row
):
    if data.teacher_id is not None:
        stmt = select(Teachers.uuid).where(Teachers.uuid == data.teacher_id)
        result = await session.scalar(stmt)
        if result is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Teacher not found")
    for key, value in data.model_dump(exclude_unset=True).items():
        if key == "translations":
            work_experience.translations.update(**data.translations)
        else:
            setattr(work_experience, key, value)
    await session.commit()
    return work_experience


async def delete_work_experience(session: AsyncSession, uuids: set[UUID]):
    stmt = select(WorkExperience.uuid).where(WorkExperience.uuid.in_(uuids))
    result = await session.scalars(stmt)
    existing_uuids = set(result)
    if missing := uuids - existing_uuids:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, detail=f"Missing UUIDs: {missing}"
        )
    else:
        stmt = delete(WorkExperience).where(WorkExperience.uuid.in_(uuids))
        await session.execute(stmt)
        await session.commit()
