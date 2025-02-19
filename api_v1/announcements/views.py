from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from .schemas import CreateAnnouncement, GetAnnouncement
from core.settings import db_sessions
from . import crud

router = APIRouter(prefix="/announcements", tags=["Announcements"])


@router.get("/", response_model=list[GetAnnouncement])
async def get_announcements(
    session: AsyncSession = Depends(db_sessions.session_dependency),
):
    data = await crud.get_all_announcements(session=session)
    print(data)
    return data


@router.post("/", response_model=GetAnnouncement)
async def create_announcement(
    data: CreateAnnouncement = Depends(CreateAnnouncement),
    session: AsyncSession = Depends(db_sessions.session_dependency),
):
    data = await crud.create_announcement(data=data, session=session)
    return data
