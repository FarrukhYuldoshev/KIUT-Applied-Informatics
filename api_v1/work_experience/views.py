from typing import Optional, Annotated
from fastapi import APIRouter, Depends, Body
from fastapi.params import Query
from sqlalchemy.ext.asyncio import AsyncSession
from .schemas import (
    GetWorkExperience,
    CreateWorkExperience,
    UpdateWorkExperience,
    Languages,
)
from core.settings import db_sessions
from uuid import UUID
from . import crud
from demo_auth import get_active_user

router = APIRouter(prefix="/teachers", tags=["Teachers API (Work Experiences)"])


@router.get(
    "/work-experience/",
    response_model=list[GetWorkExperience],
    response_model_exclude_unset=True,
)
async def get_work_experiences(
    lang: Annotated[Languages, Query(alias="lang")] = None,
    session: AsyncSession = Depends(db_sessions.session_dependency),
):
    data = await crud.get_all_work_experiences(session=session)
    return [crud.convert_sql_model_to_base_model(obj, lang=lang) for obj in data]


@router.get(
    "/work-experience/{work_experience_id}",
    response_model=GetWorkExperience,
    response_model_exclude_unset=True,
)
async def get_work_experience(
    lang: Annotated[Languages, Query(alias="lang")] = None,
    work_experience=Depends(crud.get_work_experience),
):
    if lang is not None:
        return await crud.convert_sql_model_to_base_model(work_experience, lang)
    else:
        return work_experience


@router.post(
    "/work-experience/",
    response_model=GetWorkExperience,
    response_model_exclude_unset=True,
)
async def create_work_experience(
    input_data: CreateWorkExperience,
    user=Depends(get_active_user),
    session: AsyncSession = Depends(db_sessions.session_dependency),
):
    data = await crud.create_work_experience(data=input_data, session=session)
    return data


@router.patch(
    "/work-experience/{work_experience_id}",
    response_model=GetWorkExperience,
    response_model_exclude_unset=True,
)
async def update_work_experience(
    data: UpdateWorkExperience,
    work_experience=Depends(crud.get_work_experience),
    session: AsyncSession = Depends(db_sessions.session_dependency),
    user=Depends(get_active_user),
):
    result = await crud.update_work_experience(
        work_experience=work_experience, data=data, session=session
    )
    return result


@router.delete("/work-experience/", status_code=204)
async def delete_work_experiences(
    data: Annotated[set[UUID], Body(...)],
    session: AsyncSession = Depends(db_sessions.session_dependency),
    user=Depends(get_active_user),
):
    await crud.delete_work_experience(session=session, uuids=data)
