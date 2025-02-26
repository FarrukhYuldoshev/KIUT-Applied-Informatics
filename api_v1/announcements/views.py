from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession

from core.models.enumrators import Languages
from .schemas import (
    CreateAnnouncement,
    GetAnnouncement,
    UpdateAnnouncement,
    UploadImagesToUpdateAnnouncement,
    DeleteAnnouncement,
    GetAnnouncementWithSelectedLanguage,
)
from core.settings import db_sessions
from . import crud

router = APIRouter(prefix="/announcements", tags=["Announcements"])


@router.get(
    "/",
    response_model=list[GetAnnouncement] | list[GetAnnouncementWithSelectedLanguage],
)
async def get_announcements(
    lang: Languages = Query(None, alias="lang"),
    session: AsyncSession = Depends(db_sessions.session_dependency),
):
    data = await crud.get_all_announcements(session=session, lang=lang)
    return data


@router.post("/", response_model=GetAnnouncementWithSelectedLanguage)
async def create_announcement(
    lang: Languages = Query(..., alias="lang"),
    data: CreateAnnouncement = Depends(CreateAnnouncement),
    session: AsyncSession = Depends(db_sessions.session_dependency),
):
    data = await crud.create_announcement(data=data, session=session, lang=lang)
    return data


@router.get(
    "/{announcement_id}",
    response_model=GetAnnouncement | GetAnnouncementWithSelectedLanguage,
)
async def get_announcement(announcement=Depends(crud.get_announcement)):
    return announcement


@router.post("/{announcement_id}", response_model=GetAnnouncement)
async def append_images_to_announcement(
    data: UploadImagesToUpdateAnnouncement = Depends(UploadImagesToUpdateAnnouncement),
    announcement=Depends(crud.get_announcement),
    session: AsyncSession = Depends(db_sessions.session_dependency),
):
    result = await crud.append_images(
        announcement=announcement, data=data, session=session
    )
    return result


@router.patch("/{announcement_id}", response_model=GetAnnouncement)
async def update_announcement(
    data: UpdateAnnouncement,
    announcement=Depends(crud.get_announcement),
    session: AsyncSession = Depends(db_sessions.session_dependency),
):
    result = await crud.update_announcement(
        data=data, announcement=announcement, session=session
    )
    return result


@router.delete("/", status_code=204)
async def delete_announcement(
    data: DeleteAnnouncement,
    session: AsyncSession = Depends(db_sessions.session_dependency),
):
    await crud.delete_announcement(data=data, session=session)
