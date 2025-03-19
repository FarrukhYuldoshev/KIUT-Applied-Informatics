from fastapi import HTTPException
from sqlalchemy import insert, select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette import status

from core.models.enumrators import Languages
from .schemas import CreateAcademicProgram, GetAcademicProgramsWithSubjects
from core.models import AcademicPrograms
from uuid import UUID as uuid4
from api_v1.subjects.crud import get_subjects_of_academic_program


async def set_details_to_academic_program(
    academic_program: AcademicPrograms,
    session: AsyncSession,
    language: Languages = None,
):
    subjects = await get_subjects_of_academic_program(
        academic_program_id=academic_program.uuid, lang=language, session=session
    )
    response_model = GetAcademicProgramsWithSubjects(
        uuid=academic_program.uuid,
        year_of_study=academic_program.year_of_study,
        subjects=subjects,
    )
    if language is not None:
        response_model.title = academic_program.translations.get(language, {}).get(
            "title"
        )
        response_model.program = academic_program.translations.get(language, {}).get(
            "program"
        )
        response_model.study_format = academic_program.translations.get(
            language, {}
        ).get("study_format")
    else:
        response_model.translations = academic_program.translations
    return response_model


async def create_academic_program(data: CreateAcademicProgram, session: AsyncSession):
    stmt = (
        insert(AcademicPrograms).values(**data.model_dump()).returning(AcademicPrograms)
    )
    result = await session.scalar(stmt)
    await session.commit()
    return result


async def get_academic_program(uuid: uuid4, session: AsyncSession) -> AcademicPrograms:
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
