from fastapi import HTTPException
from sqlalchemy import insert, select, delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from starlette import status

from api_v1.subjects.schemas import CreateSubject
from core.models import Subjects
import asyncpg.exceptions
from uuid import UUID as uuid4


async def create_subject(data: CreateSubject, session: AsyncSession):
    stmt = insert(Subjects).values(**data.model_dump()).returning(Subjects)
    try:
        subject = await session.scalar(stmt)
        await session.commit()
        return subject
    except IntegrityError as e:
        await session.rollback()
        if "foreign key" in str(e.orig).lower():
            raise HTTPException(
                status_code=400,
                detail=f"Academic Program not found with {data.academic_program_id} id",
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Bad request",
            )


async def get_all_subjects(session: AsyncSession):
    return await session.scalars(select(Subjects))


async def get_subject(uuid: uuid4, session: AsyncSession):
    stmt = (
        select(Subjects)
        .options(joinedload(Subjects.academic_program))
        .where(Subjects.uuid == uuid)
    )
    return await session.scalar(stmt)


async def delete_subjects(input_uuids: set[uuid4], session: AsyncSession):
    stmt = select(Subjects.uuid).where(Subjects.uuid.in_(input_uuids))
    result = await session.scalars(stmt)
    existing_uuids = set(result)
    if missing := input_uuids - existing_uuids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Bad request missing UUIDs: {missing}",
        )
    else:
        stmt = delete(Subjects).where(Subjects.uuid.in_(input_uuids))
        await session.execute(stmt)
        await session.commit()
