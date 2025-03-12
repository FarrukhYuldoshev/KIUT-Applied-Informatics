from typing import Annotated, Any, Coroutine
from fastapi.params import Query
from sqlalchemy import select, delete, insert, Row, Sequence, update, ScalarResult
from sqlalchemy.ext.asyncio import AsyncSession
from core.models import Education, Teachers
from core.settings import db_sessions
from fastapi import HTTPException, Depends, Path
from uuid import UUID

from core.models.enumrators import Languages
from .schemas import (
    CreateEducation,
    UpdateEducation,
    GetEducation,
)
from starlette import status


def convert_sql_model_to_base_model(
    education: Education, lang: Languages = None
) -> GetEducation:
    response_model = GetEducation(
        uuid=education.uuid,
        from_date=education.from_date,
        to_date=education.to_date,
        teacher_id=education.teacher_id,
    )
    if lang is not None:
        response_model.place = education.translations.get(lang, {}).get("place")
        response_model.degree = education.translations.get(lang, {}).get("degree")
    else:
        response_model.translations = education.translations
    return response_model


async def get_education_of_teacher(
    session: AsyncSession, teacher_id: UUID, lang: Languages = None
) -> list[GetEducation]:
    stmt = (
        select(Education)
        .where(Education.teacher_id == teacher_id)
        .order_by(Education.from_date.desc(), Education.to_date.desc())
    )
    result = await session.scalars(stmt)
    return [convert_sql_model_to_base_model(obj, lang=lang) for obj in result]


async def create_education(session: AsyncSession, data: CreateEducation) -> Education:
    stmt = select(Teachers.uuid).where(Teachers.uuid == data.teacher_id)
    teacher_id = await session.scalar(stmt)
    if teacher_id is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Teacher not found"
        )
    else:
        stmt = insert(Education).values(**data.model_dump()).returning(Education)
        result = await session.scalar(stmt)
        await session.commit()
        return result


async def get_education(
    education_id: Annotated[UUID, Path(alias="education_id")],
    session: AsyncSession = Depends(db_sessions.session_dependency),
) -> Education:

    stmt = select(Education).where(Education.uuid == education_id)
    result = await session.scalar(stmt)
    if result is None:
        raise HTTPException(status_code=404, detail="Education not found")
    else:
        return result


async def get_all_educations(session: AsyncSession) -> ScalarResult[Education]:
    stmt = select(Education)
    result = await session.scalars(stmt)
    return result


async def update_education(
    session: AsyncSession, data: UpdateEducation, education: Education
):
    if data.teacher_id is not None:
        stmt = select(Teachers.uuid).where(Teachers.uuid == data.teacher_id)
        result = await session.scalar(stmt)
        if result is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Teacher not found")
    for key, value in data.model_dump(exclude_unset=True).items():
        if key == "translations":
            education.translations.update(**data.translations)
        else:
            setattr(education, key, value)
    await session.commit()
    return education


async def delete_education(session: AsyncSession, uuids: set[UUID]):
    stmt = select(Education.uuid).where(Education.uuid.in_(uuids))
    result = await session.scalars(stmt)
    existing_uuids = set(result)
    if missing := uuids - existing_uuids:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, detail=f"Missing UUIDs: {missing}"
        )
    else:
        stmt = delete(Education).where(Education.uuid.in_(uuids))
        await session.execute(stmt)
        await session.commit()
