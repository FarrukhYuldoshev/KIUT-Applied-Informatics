from typing import List, Annotated

from fastapi import APIRouter, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession

from core.models.enumrators import Languages
from .schemas import CreateSubject, GetSubject, GetSubjectWithAcademicProgram, OnlyUUID
from . import crud
from core.settings import db_sessions
from fastapi import Depends
from uuid import UUID as uuid4

router = APIRouter(prefix="/subjects", tags=["Subjects"])


@router.post(
    "/", response_model=GetSubject, response_model_exclude_unset=True, status_code=201
)
async def create_subject(
    data: CreateSubject, session: AsyncSession = Depends(db_sessions.session_dependency)
):
    result = await crud.create_subject(data=data, session=session)
    return result


@router.get(
    "/",
    response_model=List[GetSubject],
    response_model_exclude_unset=True,
)
async def get_all_subjects(
    lang: Languages = Query(alias="lang", default=None),
    session: AsyncSession = Depends(db_sessions.session_dependency),
):
    result = await crud.get_all_subjects(session=session)
    if lang is not None:
        subjects: list[GetSubject] = []
        for subject in result:
            subjects.append(
                GetSubject(
                    uuid=subject.uuid,
                    credits=subject.credits,
                    semester=subject.semester,
                    academic_program_id=subject.academic_program_id,
                    **subject.translations[lang.value],
                )
            )
        return subjects
    return result


@router.get(
    "/{uuid}",
    response_model=GetSubjectWithAcademicProgram,
    response_model_exclude_unset=True,
)
async def get_subject(
    uuid: uuid4,
    session: AsyncSession = Depends(db_sessions.session_dependency),
    lang: Languages = Query(alias="lang", default=None),
):
    subject = await crud.get_subject(uuid=uuid, session=session)
    if lang is not None and subject is not None:
        result = GetSubjectWithAcademicProgram(
            uuid=subject.uuid,
            credits=subject.credits,
            semester=subject.semester,
            academic_program_id=subject.academic_program_id,
            academic_program=(
                {"uuid": subject.academic_program.uuid}
                if subject.academic_program.uuid is not None
                else None
            ),
            **subject.translations[lang.value],
        )
        return result
    return subject


@router.delete("/", status_code=204)
async def delete_subject(
    uuids: Annotated[set[uuid4], Body()],
    session: AsyncSession = Depends(db_sessions.session_dependency),
):
    await crud.delete_subjects(input_uuids=uuids, session=session)
