from fastapi import HTTPException
from sqlalchemy import insert, select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette import status

from core.models.enumrators import Languages
from .schemas import CreateAcademicProgram
from core.models import AcademicPrograms
from uuid import UUID as uuid4


async def create_academic_program(data: CreateAcademicProgram, session: AsyncSession):
    stmt = (
        insert(AcademicPrograms).values(**data.model_dump()).returning(AcademicPrograms)
    )
    result = await session.scalar(stmt)
    await session.commit()
    return result


async def get_academic_program(uuid: uuid4, session: AsyncSession):
    stmt = (
        select(AcademicPrograms)
        .options(selectinload(AcademicPrograms.subjects))
        .where(AcademicPrograms.uuid == uuid)
    )
    result = await session.scalar(stmt)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    else:
        return result


async def get_all_academic_programs(session: AsyncSession):
    stmt = select(AcademicPrograms).options(selectinload(AcademicPrograms.subjects))
    return await session.scalars(stmt)


async def delete_academic_program(input_uuids: set[uuid4], session: AsyncSession):
    stmt = select(AcademicPrograms.uuid).where(AcademicPrograms.uuid.in_(input_uuids))
    result = await session.scalars(stmt)
    existing_uuids = set(result)
    if missing := input_uuids - existing_uuids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Bad request missing UUIDs: {missing}",
        )
    else:
        stmt = delete(AcademicPrograms).where(AcademicPrograms.uuid.in_(input_uuids))
        await session.execute(stmt)
        await session.commit()
