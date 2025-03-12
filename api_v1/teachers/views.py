from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query

from core.models.enumrators import Languages
from core.settings import db_sessions
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from .schemas import (
    CreateTeacher,
    GetTeachers,
    GetTeachersWithResearchInterests,
    UpdateTeacher,
)
from . import crud
import uuid
from demo_auth import get_active_user

router = APIRouter(prefix="/teachers", tags=["Teachers API"])


@router.post(
    "/",
    response_model=GetTeachers,
    status_code=status.HTTP_201_CREATED,
    response_model_exclude_unset=True,
)
async def create_teacher(
    data: CreateTeacher,
    user=Depends(get_active_user),
    session: AsyncSession = Depends(db_sessions.session_dependency),
):
    result = await crud.create_teacher(session=session, data=data)
    return result


@router.post("/{uuid}", response_model=GetTeachers)
async def set_image_to_teacher(result=Depends(crud.set_image)):
    return result


@router.get("/", response_model=list[GetTeachers], response_model_exclude_unset=True)
async def get_all_teachers(
    session: AsyncSession = Depends(db_sessions.session_dependency),
):
    result = await crud.get_all_teachers(session=session)
    return result


@router.get(
    "/{teacher_id}",
    response_model=GetTeachersWithResearchInterests,
    response_model_exclude_unset=True,
)
async def get_teacher(
    teacher_id: Annotated[uuid.UUID, Path(description="Teacher uuid")],
    session: AsyncSession = Depends(db_sessions.session_dependency),
    lang: Annotated[Languages, Query(alias="lang")] = None,
):
    result = await crud.get_teacher_or_none(
        teacher_id=teacher_id, session=session, lang=lang
    )
    return result


@router.patch("/{teacher_id}", response_model=GetTeachersWithResearchInterests)
async def update_teacher(
    teacher_id: Annotated[uuid.UUID, Path(description="Teacher uuid")],
    data: UpdateTeacher,
    session: AsyncSession = Depends(db_sessions.session_dependency),
    user=Depends(get_active_user),
):
    result = await crud.update_teacher(
        teacher_id=teacher_id, data=data, session=session
    )
    return result


@router.delete("/{teacher_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_teacher(
    teacher_id: uuid.UUID,
    session: AsyncSession = Depends(db_sessions.session_dependency),
    user=Depends(get_active_user),
):
    teacher = await crud.get_teacher_or_none(teacher_id=teacher_id, session=session)
    await crud.delete_teacher(teacher=teacher, session=session)
