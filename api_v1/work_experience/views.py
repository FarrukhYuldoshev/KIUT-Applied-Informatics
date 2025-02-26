from typing import Optional, Annotated
from fastapi import APIRouter, Depends, Body
from fastapi.params import Query
from sqlalchemy.ext.asyncio import AsyncSession
from .schemas import (
    GetWorkExperience,
    CreateWorkExperience,
    UpdateWorkExperience,
    GetWorkExperienceWithSelectedLanguage,
    Languages,
)
from core.settings import db_sessions
from uuid import UUID
from . import crud
from demo_auth import get_active_user

router = APIRouter(prefix="/teachers", tags=["Teachers API (Work Experiences)"])


@router.get(
    "/work-experience/",
    response_model=list[GetWorkExperience] | list[GetWorkExperienceWithSelectedLanguage],
)
async def get_work_experiences(
    lang: Annotated[Languages, Query(alias="lang")] = None,
    session: AsyncSession = Depends(db_sessions.session_dependency),
):
    data = await crud.get_all_work_experiences(session=session, lang=lang)
    return data


@router.get(
    "/work-experience/{work_experience_id}",
    response_model=GetWorkExperience | GetWorkExperienceWithSelectedLanguage,
)
async def get_work_experience(
    work_experience=Depends(crud.get_work_experience),
):
    return work_experience


@router.post("/work-experience/", response_model=GetWorkExperienceWithSelectedLanguage)
async def create_work_experience(
    user=Depends(get_active_user),
    input_data: CreateWorkExperience = Depends(CreateWorkExperience),
    session: AsyncSession = Depends(db_sessions.session_dependency),
):
    print(input_data.lang)
    data = await crud.create_work_experience(data=input_data, session=session)
    return data


@router.patch("/work-experience/{work_experience_id}", response_model=GetWorkExperience)
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
async def delete_education(
    data: Annotated[set[UUID], Body(...)],
    session: AsyncSession = Depends(db_sessions.session_dependency),
    user=Depends(get_active_user),
):
    await crud.delete_work_experience(session=session, uuids=data)
