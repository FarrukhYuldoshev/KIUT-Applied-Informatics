from typing import Optional, Annotated
from fastapi import APIRouter, Depends, Body
from fastapi.params import Query
from sqlalchemy.ext.asyncio import AsyncSession
from .schemas import (
    GetEducation,
    CreateEducation,
    UpdateEducation,
    GetEducationWithSelectedLanguage,
    Languages,
)
from core.settings import db_sessions
from uuid import UUID
from . import crud
from demo_auth import get_active_user

router = APIRouter(prefix="/teachers", tags=["Teachers API (Educations)"])


@router.get(
    "/educations/",
    response_model=list[GetEducation] | list[GetEducationWithSelectedLanguage],
)
async def get_educations(
    lang: Annotated[Languages, Query(alias="lang")] = None,
    session: AsyncSession = Depends(db_sessions.session_dependency),
):
    data = await crud.get_all_educations(session=session, lang=lang)
    return data


@router.get(
    "/educations/{education_id}",
    response_model=GetEducation | GetEducationWithSelectedLanguage,
)
async def get_educations(
    education=Depends(crud.get_education),
):
    return education


@router.post("/educations/", response_model=GetEducationWithSelectedLanguage)
async def create_education(
    user=Depends(get_active_user),
    data: CreateEducation = Depends(CreateEducation),
    session: AsyncSession = Depends(db_sessions.session_dependency),
):
    data = await crud.create_education(data=data, session=session)
    return data


@router.patch("/educations/{education_id}", response_model=GetEducation)
async def update_education_patch(
    data: UpdateEducation,
    education=Depends(crud.get_education),
    session: AsyncSession = Depends(db_sessions.session_dependency),
    user=Depends(get_active_user),
):
    result = await crud.update_education(
        education=education, data=data, session=session
    )
    return result


@router.delete("/educations/", status_code=204)
async def delete_education(
    data: Annotated[set[UUID], Body(...)],
    session: AsyncSession = Depends(db_sessions.session_dependency),
    user=Depends(get_active_user),
):
    await crud.delete_education(session=session, uuids=data)
