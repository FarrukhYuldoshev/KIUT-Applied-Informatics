from typing import Annotated

from fastapi import HTTPException, Path, Depends
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from api_v1.teachers.crud import create_file
from .schemas import CreateAnnouncement
from datetime import date
from pathlib import Path as Pathlib
from core.models import Announcements
from uuid import UUID
from core.settings import db_sessions
UPLOAD_DIR = Pathlib("static/announcements")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


async def get_announcement(announcement_id: Annotated[UUID, Path(alias="announcement_id")], session: AsyncSession = Depends(db_sessions.session_dependency)) -> Announcements:
    stmt = select(Announcements).where(Announcements.uuid == announcement_id)
    result = await session.scalar(stmt)
    if result is None:
        raise HTTPException(status_code=404, detail="Announcement not found")
    return result

async def create_announcement(data: CreateAnnouncement, session: AsyncSession):
    if data.files is None:
        data.files = [(UPLOAD_DIR / "default.png").__str__()]
    else:
        images = data.files
        upload_url = UPLOAD_DIR / date.today().strftime("%Y-%m-%d")
        upload_url.mkdir(parents=True, exist_ok=True)
        data.files = [
            await create_file(file=image, upload_path=upload_url) for image in images
        ]
    stmt = (
        insert(Announcements)
        .values(title=data.title, description=data.description, images=data.files)
        .returning(Announcements)
    )
    result = await session.execute(stmt)
    await session.commit()
    return result.scalar()


async def get_all_announcements(session: AsyncSession):
    stmt = select(Announcements)
    result = await session.scalars(stmt)
    return result

# async def update_announcement(announcement: Announcements, session: AsyncSession):
#     if announcement.images is not None:
#
#     session.add(announcement)
#     await session.commit()