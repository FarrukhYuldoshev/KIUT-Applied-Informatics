from typing import Optional, Annotated
from fastapi import APIRouter, Depends, Body
from fastapi.params import Query
from sqlalchemy.ext.asyncio import AsyncSession
from .schemas import (
    GetEducation,
    CreateEducation,
    UpdateEducation,
    Languages,
)
from core.settings import db_sessions
from uuid import UUID
from . import crud
from demo_auth import get_active_user

router = APIRouter(prefix="/teachers", tags=["Teachers API (Educations)"])


@router.get(
    "/education/",
    response_model=list[GetEducation],
    response_model_exclude_unset=True,
)
async def get_educations(
    lang: Annotated[Languages, Query(alias="lang")] = None,
    session: AsyncSession = Depends(db_sessions.session_dependency),
):
    data = await crud.get_all_educations(session=session)
    return [crud.convert_sql_model_to_base_model(obj, lang=lang) for obj in data]


@router.get(
    "/education/{education_id}",
    response_model=GetEducation,
    response_model_exclude_unset=True,
)
async def get_education(
    lang: Annotated[Languages, Query(alias="lang")] = None,
    education=Depends(crud.get_education),
):
    return crud.convert_sql_model_to_base_model(education=education, lang=lang)


@router.post(
    "/education/",
    response_model=GetEducation,
    response_model_exclude_unset=True,
)
async def create_education(
    input_data: CreateEducation,
    user=Depends(get_active_user),
    session: AsyncSession = Depends(db_sessions.session_dependency),
):
    data = await crud.create_education(data=input_data, session=session)
    return data


@router.patch(
    "/education/{education_id}",
    response_model=GetEducation,
    response_model_exclude_unset=True,
)
async def update_education(
    data: UpdateEducation,
    education=Depends(crud.get_education),
    session: AsyncSession = Depends(db_sessions.session_dependency),
    user=Depends(get_active_user),
):
    result = await crud.update_education(
        education=education, data=data, session=session
    )
    return result


@router.delete("/education/", status_code=204)
async def delete_education(
    data: Annotated[set[UUID], Body(...)],
    session: AsyncSession = Depends(db_sessions.session_dependency),
    user=Depends(get_active_user),
):
    await crud.delete_education(session=session, uuids=data)
