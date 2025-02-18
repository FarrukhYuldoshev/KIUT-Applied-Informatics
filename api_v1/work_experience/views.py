from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .schemas import GetWorkExperience, CreateWorkExperience, UpdateWorkExperience
from core.settings import db_sessions
from uuid import UUID
from . import crud
from demo_auth import get_active_user
router = APIRouter(prefix="/teachers", tags=["Teachers API (Work Experience)"])


@router.get("/work-experience/", response_model=list[GetWorkExperience])
async def get_all_work_experiences(
    session: AsyncSession = Depends(db_sessions.session_dependency),
):
    data = await crud.get_all_work_experience(session=session)
    return data


@router.get("/work-experience/{work_experience_id}", response_model=GetWorkExperience)
async def get_work_experience(
    work_experience_id: Optional[UUID] = None,
    session: AsyncSession = Depends(db_sessions.session_dependency),
):
    data = await crud.get_work_experience(
        work_experience_id=work_experience_id, session=session
    )
    return data


@router.post("/work-experience/", response_model=GetWorkExperience)
async def create_work_experience(
    user = Depends(get_active_user),
    data: CreateWorkExperience = Depends(CreateWorkExperience),
    session: AsyncSession = Depends(db_sessions.session_dependency),
):
    data = await crud.create_work_experience(data=data, session=session)
    return data


@router.patch("/work-experience/{work_experience_id}", response_model=GetWorkExperience)
async def update_work_experience(
    data: UpdateWorkExperience,
    work_experience_id: UUID,
    session: AsyncSession = Depends(db_sessions.session_dependency),
    user = Depends(get_active_user),
):
    result = await crud.update_education(
        work_experience_id=work_experience_id, data=data, session=session, partial=True
    )
    return result


@router.put(
    "/work-experience/{work_experience_id}", response_model=UpdateWorkExperience
)
async def update_work_experience(
    data: UpdateWorkExperience,
    work_experience_id: UUID,
    session: AsyncSession = Depends(db_sessions.session_dependency),
    user = Depends(get_active_user),
):
    result = await crud.update_education(
        work_experience_id=work_experience_id, data=data, session=session, partial=False
    )
    return result


@router.delete("/work-experience/{education_id}", status_code=204)
async def delete_education(
    work_experience_id: UUID,
    session: AsyncSession = Depends(db_sessions.session_dependency),
    user = Depends(get_active_user),
):
    await crud.delete_work_experience(
        work_experience_id=work_experience_id, session=session
    )
