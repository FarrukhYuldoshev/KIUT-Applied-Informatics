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
    "/",
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
    "/",
    response_model=list[GetAcademicPrograms],
    response_model_exclude_unset=True,
)
async def get_all_academic_programs(
    lang: Languages = Query(alias="lang", default=None),
    session: AsyncSession = Depends(db_sessions.session_dependency),
):
    result = await crud.get_all_academic_programs(session=session)
    # programs: list[GetAcademicProgramsWithSubjects] = []
    # if lang is not None:
    #     for obj in result:
    #         programs.append(
    #             GetAcademicProgramsWithSubjects(
    #                 subjects=[{"uuid": value.uuid} for value in obj.subjects],
    #                 uuid=obj.uuid,
    #                 year_of_study=obj.year_of_study,
    #                 **obj.translations[lang.value]
    #             )
    #         )
    #     return programs
    if lang is not None:
        programs: list[GetAcademicPrograms] = []
        for obj in result:
            programs.append(
                GetAcademicPrograms(
                    uuid=obj.uuid,
                    title=obj.translations.get(lang, {}).get("title"),
                    study_format=obj.translations.get(lang, {}).get("study_format"),
                    program=obj.translations.get(lang, {}).get("program"),
                    year_of_study=obj.year_of_study,
                )
            )
        return programs
    return result


@router.get(
    "/{uuid}",
    response_model=GetAcademicProgramsWithSubjects,
    response_model_exclude_unset=True,
)
async def get_academic_program(
    uuid: UUID,
    session: AsyncSession = Depends(db_sessions.session_dependency),
    lang: Languages = Query(alias="lang", default=None),
):
    result = await crud.get_academic_program(uuid, session=session)
    response = await crud.set_details_to_academic_program(
        academic_program=result, language=lang, session=session
    )
    return response


@router.delete("/")
async def delete_academic_programs(
    uuids: Annotated[set[UUID], Body(serialization_alias="academic_programs_uuids")],
    response: Response,
    session: AsyncSession = Depends(db_sessions.session_dependency),
):
    await crud.delete_academic_program(input_uuids=uuids, session=session)
    response.status_code = status.HTTP_204_NO_CONTENT
    return response
