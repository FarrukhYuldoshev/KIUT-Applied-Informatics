from fastapi import APIRouter, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from core.settings import db_sessions
from .schemas import GetPublication, OnlyUUID, CreatePublication, UpdatePublication
from . import crud
from uuid import UUID as UUID4
from .schemas import TeacherWithPublications
from demo_auth import get_active_user
router = APIRouter(prefix="/publications", tags=["Teachers API (Publications)"])


@router.get("/", response_model=list[GetPublication])
async def get_all_publications(
    session: AsyncSession = Depends(db_sessions.session_dependency),
):
    result = await crud.get_all_publications(session=session)
    return result


@router.get("/{publication_id}", response_model=GetPublication)
async def get_publication(publication=Depends(crud.get_publication)):
    return publication


@router.post("/{teacher_id}", response_model=TeacherWithPublications)
async def set_publications_to_teacher(
    publications: list[OnlyUUID],
    teacher_id: UUID4 = Depends(crud.get_teacher_or_none),
    session: AsyncSession = Depends(db_sessions.session_dependency),
    user = Depends(get_active_user),
):
    result = await crud.set_publications_to_teacher(
        teacher_id=teacher_id, session=session, publications=publications
    )
    return result


@router.post("/", response_model=GetPublication)
async def create_publication(
    user = Depends(get_active_user),
    data: CreatePublication = Depends(CreatePublication),
    session: AsyncSession = Depends(db_sessions.session_dependency),
):
    result = await crud.create_publication(data=data, session=session)
    return result


@router.patch("/{publication_id}", response_model=GetPublication)
async def update_publication(
    data: UpdatePublication,
    publication=Depends(crud.get_publication),
    session: AsyncSession = Depends(db_sessions.session_dependency),
    user = Depends(get_active_user),
):
    result = await crud.update_publication(
        publication=publication, data=data, session=session, partial=True
    )
    return result


@router.put("/{publication_id}", response_model=GetPublication)
async def update_publication(
    data: UpdatePublication,
    publication=Depends(crud.get_publication),
    session: AsyncSession = Depends(db_sessions.session_dependency),
    user = Depends(get_active_user),
):
    result = await crud.update_publication(
        publication=publication, data=data, session=session, partial=False
    )
    return result


@router.delete("/{publication_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_publication(
    user = Depends(get_active_user),
    publication=Depends(crud.get_publication),
    session: AsyncSession = Depends(db_sessions.session_dependency),
):
    await crud.delete_publication(
        publication=publication,
        session=session,
    )
