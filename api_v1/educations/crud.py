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
    CreateEducation,
    UpdateEducation,
)
from starlette import status


async def create_education(session: AsyncSession, data: CreateEducation):
    translation: dict[Languages, dict[str, str]] = {
        data.lang: {"place": data.place, "degree": data.degree.value}
    }
    stmt = select(Teachers.uuid).where(Teachers.uuid == data.teacher_id)
    teacher_id = await session.scalar(stmt)
    if teacher_id is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Teacher not found"
        )
    else:
        stmt = (
            insert(WorkExperience)
            .values(
                from_date=data.from_date,
                to_date=data.to_date,
                teacher_id=teacher_id,
                translations=translation,
            )
            .returning(
                WorkExperience.uuid,
                WorkExperience.translations[data.lang.value]["place"].label("place"),
                WorkExperience.translations[data.lang.value]["degree"].label("degree"),
                WorkExperience.from_date,
                WorkExperience.to_date,
                WorkExperience.teacher_id,
            )
        )
        result = await session.execute(stmt)
        await session.commit()
        return result.one()


async def get_educations_of_teacher(
    teacher_id: UUID,
    session: AsyncSession,
    lang: Languages = None,
):
    if lang is None:
        stmt = select(WorkExperience).where(WorkExperience.teacher_id == teacher_id)
        result = await session.scalars(stmt)
        return result
    else:
        stmt = select(
            WorkExperience.uuid,
            WorkExperience.from_date,
            WorkExperience.to_date,
            WorkExperience.translations[lang.value]["place"].label("place"),
            WorkExperience.translations[lang.value]["degree"].label("degree"),
            WorkExperience.teacher_id,
        )
        result = await session.execute(stmt)
        return result.all()


async def get_education(
    edu_id: Annotated[UUID, Path(alias="education_id")],
    lang: Annotated[Languages, Query(alias="lang")] = None,
    session: AsyncSession = Depends(db_sessions.session_dependency),
) -> Row:
    if lang is None:
        stmt = select(
            WorkExperience.uuid,
            WorkExperience.from_date,
            WorkExperience.to_date,
            WorkExperience.teacher_id,
            WorkExperience.translations,
        ).where(WorkExperience.uuid == edu_id)
        result = await session.execute(stmt)
        edu = result.one_or_none()
    else:
        stmt = select(
            WorkExperience.uuid,
            WorkExperience.from_date,
            WorkExperience.to_date,
            WorkExperience.translations[lang.value]["place"].label("place"),
            WorkExperience.translations[lang.value]["degree"].label("degree"),
            WorkExperience.teacher_id,
        ).where(WorkExperience.uuid == edu_id)
        result = await session.execute(stmt)
        edu = result.one_or_none()
        print(edu)
    if edu is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Education not found")
    else:
        return edu


async def get_all_educations(
    session: AsyncSession, lang: Languages = None
) -> Sequence[Row]:
    if lang is None:
        stmt = select(
            WorkExperience.uuid,
            WorkExperience.from_date,
            WorkExperience.to_date,
            WorkExperience.teacher_id,
            WorkExperience.translations,
        )
        edu = await session.execute(stmt)
    else:
        stmt = select(
            WorkExperience.uuid,
            WorkExperience.from_date,
            WorkExperience.to_date,
            WorkExperience.translations[lang.value]["place"].label("place"),
            WorkExperience.translations[lang.value]["degree"].label("degree"),
            WorkExperience.teacher_id,
        )
        edu = await session.execute(stmt)
    return edu.all()


async def update_education(
    session: AsyncSession, data: UpdateEducation, education: Row
):
    if data.teacher_id is not None:
        stmt = select(Teachers.uuid).where(Teachers.uuid == data.teacher_id)
        result = await session.scalar(stmt)
        if result is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Teacher not found")

    existing_edu_id = education.__getattr__("uuid")
    stmt = (
        update(WorkExperience)
        .values(**data.model_dump(exclude_unset=True))
        .where(WorkExperience.uuid == existing_edu_id)
    ).returning(WorkExperience)
    result = await session.scalar(stmt)
    await session.commit()
    return result


async def delete_education(session: AsyncSession, uuids: set[UUID]):
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
