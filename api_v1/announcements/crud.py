from typing import Annotated

from fastapi import HTTPException, Path, Depends
from sqlalchemy import insert, select, delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from api_v1.teachers.crud import create_file
from .schemas import (
    CreateAnnouncement,
    UploadImagesToUpdateAnnouncement,
    UpdateAnnouncement,
    DeleteAnnouncement,
)
from datetime import date
from pathlib import Path as Pathlib
from core.models import Announcements
from uuid import UUID
from core.settings import db_sessions

UPLOAD_DIR = Pathlib("static/announcements")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


async def get_announcement(
    announcement_id: Annotated[UUID, Path(alias="announcement_id")],
    session: AsyncSession = Depends(db_sessions.session_dependency),
) -> Announcements:
    stmt = select(Announcements).where(Announcements.uuid == announcement_id)
    result = await session.scalar(stmt)
    if result is None:
        raise HTTPException(status_code=404, detail="Announcement not found")
    return result


async def create_announcement(data: CreateAnnouncement, session: AsyncSession):
    if data.files is None:
        data.files = [Pathlib("default.png").__str__()]
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


async def append_images(
    announcement: Announcements,
    data: UploadImagesToUpdateAnnouncement,
    session: AsyncSession,
):
    upload_url = UPLOAD_DIR / date.today().strftime("%Y-%m-%d")
    upload_url.mkdir(parents=True, exist_ok=True)
    files = [
        await create_file(file=image, upload_path=upload_url) for image in data.files
    ]
    announcement.images = announcement.images + files
    session.add(announcement)
    await session.commit()
    return announcement


async def update_announcement(
    announcement: Announcements,
    data: UpdateAnnouncement,
    session: AsyncSession,
    partial=True,
):
    for k, v in data.model_dump(exclude_unset=partial).items():
        setattr(announcement, k, v)
    session.add(announcement)
    try:
        await session.commit()
    except IntegrityError as e:
        raise HTTPException(status_code=400, detail="Bad request")
    return announcement


async def delete_announcement(data: DeleteAnnouncement, session: AsyncSession):
    stmt = select(Announcements.uuid).where(Announcements.uuid.in_(data.uuids))
    existing_announcements = set(await session.scalars(stmt))
    print(existing_announcements)
    if missing := data.uuids - existing_announcements:
        raise HTTPException(
            status_code=400, detail=f"Bad request! Announcement(s) not found {missing}"
        )
    else:
        stmt = delete(Announcements).where(Announcements.uuid.in_(data.uuids))
        await session.execute(stmt)
        await session.commit()
