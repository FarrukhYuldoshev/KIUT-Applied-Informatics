from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request
from starlette.responses import Response

from core.models.enumrators import Languages
from .schemas import (
    CreateAnnouncement,
    GetAnnouncement,
    UpdateAnnouncement,
    UploadImagesToUpdateAnnouncement,
    DeleteAnnouncement,
    AnnouncementsResponse,
    PaginationParams,
)

from core.settings import db_sessions
from . import crud

router = APIRouter(prefix="/announcements", tags=["Announcements"])


@router.get(
    "/",
    response_model=AnnouncementsResponse | list[GetAnnouncement],
    response_model_exclude_unset=True,
)
async def get_announcements(
    request: Request,
    lang: Languages = Query(None, alias="lang"),
    page: int = Query(None, alias="page", ge=1),
    page_size: int = Query(None, alias="page_size", ge=1),
    session: AsyncSession = Depends(db_sessions.session_dependency),
):
    data = await crud.get_all_announcements(session=session, lang=lang)
    if page is None or page_size is None:
        return data
    else:
        start = (page - 1) * page_size
        end = start + page_size
        total = await crud.count_announcements(session=session)
        pagination: dict[str, str | None] = {"previous": None, "next": None}
        if end >= total:
            pagination.update(next=None)
            if page > 1:
                pagination.update(
                    previous=str(request.url.include_query_params(page=page - 1))
                )
            else:
                pagination.update(previous=None)
        else:
            if page > 1:
                pagination.update(
                    previous=str(request.url.include_query_params(page=page - 1))
                )
            else:
                pagination.update(previous=None)
            pagination.update(next=str(request.url.include_query_params(page=page + 1)))
        pagination_params = PaginationParams(
            total=total, count=page_size, pagination=pagination
        )
        return AnnouncementsResponse(
            data=data[start:end], pagination_params=pagination_params
        )


@router.post("/", response_model=GetAnnouncement, response_model_exclude_unset=True)
async def create_announcement(
    lang: Languages = Query(..., alias="lang"),
    data: CreateAnnouncement = Depends(CreateAnnouncement),
    session: AsyncSession = Depends(db_sessions.session_dependency),
):
    data = await crud.create_announcement(data=data, session=session, lang=lang)
    return data


@router.get(
    "/{announcement_id}",
    response_model=GetAnnouncement,
    response_model_exclude_unset=True,
)
async def get_announcement(announcement=Depends(crud.get_announcement)):
    return announcement


@router.post(
    "/{announcement_id}",
    response_model=GetAnnouncement,
    response_model_exclude_unset=True,
)
async def append_images_to_announcement(
    data: UploadImagesToUpdateAnnouncement = Depends(UploadImagesToUpdateAnnouncement),
    announcement=Depends(crud.get_announcement),
    session: AsyncSession = Depends(db_sessions.session_dependency),
):
    result = await crud.append_images(
        announcement=announcement, data=data, session=session
    )
    return result


@router.patch(
    "/{announcement_id}",
    response_model=GetAnnouncement,
    response_model_exclude_unset=True,
)
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
