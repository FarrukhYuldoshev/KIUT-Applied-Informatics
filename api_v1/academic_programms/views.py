from typing import List, Annotated

from fastapi import APIRouter, Depends, Query, Body

from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.responses import Response

from core.models.enumrators import Languages
from .schemas import (
    CreateAcademicProgram,
    GetAcademicPrograms,
    GetAcademicProgramsWithSubjects,
)
from core.settings import db_sessions
from . import crud
from uuid import UUID

router = APIRouter(prefix="/academic_programs", tags=["Academic Programs"])


@router.post(
    "/academic_programs",
    response_model=GetAcademicPrograms,
    response_model_exclude_unset=True,
    status_code=status.HTTP_201_CREATED,
)
async def create_academic_program(
    data: CreateAcademicProgram,
    session: AsyncSession = Depends(db_sessions.session_dependency),
):
    result = await crud.create_academic_program(data=data, session=session)
    return result


@router.get(
    "/academic_programs",
    response_model=list[GetAcademicProgramsWithSubjects],
    response_model_exclude_unset=True,
)
async def get_all_academic_programs(
    lang: Languages = Query(alias="lang", default=None),
    session: AsyncSession = Depends(db_sessions.session_dependency),
):
    result = await crud.get_all_academic_programs(session=session)
    programs: list[GetAcademicProgramsWithSubjects] = []
    if lang is not None:
        for obj in result:
            programs.append(
                GetAcademicProgramsWithSubjects(
                    subjects=obj.subjects,
                    uuid=obj.uuid,
                    year_of_study=obj.year_of_study,
                    **obj.translations[lang.value]
                )
            )
        return programs
    return result


@router.get(
    "/academic_programs/{uuid}",
    response_model=GetAcademicProgramsWithSubjects,
    response_model_exclude_unset=True,
)
async def get_academic_program(
    uuid: UUID, session: AsyncSession = Depends(db_sessions.session_dependency)
):
    result = await crud.get_academic_program(uuid, session=session)
    return result


@router.delete("/academic_programms")
async def delete_academic_programs(
    uuids: Annotated[set[UUID], Body(serialization_alias="academic_programs_uuids")],
    response: Response,
    session: AsyncSession = Depends(db_sessions.session_dependency),
):
    await crud.delete_academic_program(input_uuids=uuids, session=session)
    response.status_code = status.HTTP_204_NO_CONTENT
    return response
