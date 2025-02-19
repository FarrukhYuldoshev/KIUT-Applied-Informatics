from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from .schemas import CreateAnnouncement
from core.settings import db_sessions
from . import crud

router = APIRouter(prefix="/announcements", tags=["Announcements"])


@router.post("/")
async def create_announcement(
    data: CreateAnnouncement = Depends(CreateAnnouncement),
    session: AsyncSession = Depends(db_sessions.session_dependency),
):
    data = await crud.create_announcement(data=data, session=session)
    pass
