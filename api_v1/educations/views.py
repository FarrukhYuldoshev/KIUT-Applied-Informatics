from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .schemas import GetEducation, CreateEducation, UpdateEducation
from core.settings import db_sessions
from uuid import UUID
from . import crud
from demo_auth import get_active_user
router = APIRouter(prefix="/teachers", tags=["Teachers API (Educations)"])


@router.get("/educations/", response_model=list[GetEducation])
async def get_educations(
    session: AsyncSession = Depends(db_sessions.session_dependency),
):
    data = await crud.get_all_educations(session=session)
    return data


@router.get("/educations/{education_id}", response_model=GetEducation)
async def get_educations(
    education_id: Optional[UUID] = None,
    session: AsyncSession = Depends(db_sessions.session_dependency),
):
    data = await crud.get_education(edu_id=education_id, session=session)
    return data


@router.post("/educations/", response_model=GetEducation)
async def create_education(
    user = Depends(get_active_user),
    data: CreateEducation = Depends(CreateEducation),
    session: AsyncSession = Depends(db_sessions.session_dependency),
):
    data = await crud.create_education(data=data, session=session)
    return data


@router.patch("/educations/{education_id}", response_model=GetEducation)
async def update_education_patch(
    data: UpdateEducation,
    education_id: UUID,
    session: AsyncSession = Depends(db_sessions.session_dependency),
    user = Depends(get_active_user),
):
    result = await crud.update_education(
        edu_uuid=education_id, data=data, session=session, partial=True
    )
    return result


@router.put("/educations/{education_id}", response_model=GetEducation)
async def update_education_put(
    data: UpdateEducation,
    education_id: UUID,
    session: AsyncSession = Depends(db_sessions.session_dependency),
    user = Depends(get_active_user),
):
    result = await crud.update_education(
        edu_uuid=education_id, data=data, session=session, partial=False
    )
    return result


@router.delete("/educations/{education_id}", status_code=204)
async def delete_education(
    education_id: UUID, 
    session: AsyncSession = Depends(db_sessions.session_dependency),
    user = Depends(get_active_user),
):
    await crud.delete_education(edu_id=education_id, session=session)
