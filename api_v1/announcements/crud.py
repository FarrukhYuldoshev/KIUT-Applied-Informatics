from typing import Annotated, Any, Sequence

from fastapi.params import Query
from sqlalchemy import Row, update
from fastapi import HTTPException, Path, Depends
from sqlalchemy import insert, select, delete, and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from api_v1.teachers.crud import create_file
from core.models.enumrators import Languages
from .schemas import (
    CreateAnnouncement,
    UploadImagesToUpdateAnnouncement,
    UpdateAnnouncement,
    DeleteAnnouncement,
)
from datetime import date, datetime
from pathlib import Path as Pathlib
from core.models import Announcements
from uuid import UUID
from core.settings import db_sessions

UPLOAD_DIR = Pathlib("static/announcements")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


async def get_announcement(
    announcement_id: Annotated[UUID, Path(alias="announcement_id")],
    lang: Annotated[Languages, Query(alias="lang")] = None,
    session: AsyncSession = Depends(db_sessions.session_dependency),
) -> Sequence[Row] | None:
    if lang is None:
        stmt = select(
            Announcements.uuid,
            Announcements.images,
            Announcements.created_at,
            Announcements.updated_at,
            Announcements.translations,
        ).where(Announcements.uuid == announcement_id)
    else:
        stmt = select(
            Announcements.uuid,
            Announcements.images,
            Announcements.translations[lang.value]["title"].label("title"),
            Announcements.translations[lang.value]["description"].label("description"),
            Announcements.created_at,
            Announcements.updated_at,
        ).where(
            and_(
                # Announcements.translations[lang.value].isnot(None),
                Announcements.uuid
                == announcement_id,
            )
        )
    result = await session.execute(stmt)
    announcement_row = result.one_or_none()
    if announcement_row is None:
        raise HTTPException(status_code=404, detail="Announcement not found")
    return announcement_row


async def create_announcement(
    data: CreateAnnouncement, session: AsyncSession, lang: Languages
) -> Sequence[Row[tuple[str, Any, Any, list[str], datetime, datetime]]]:
    if data.files is None:
        data.files = [Pathlib("default.png").__str__()]
    else:
        images = data.files
        upload_url = UPLOAD_DIR / date.today().strftime("%Y-%m-%d")
        upload_url.mkdir(parents=True, exist_ok=True)
        data.files = [
            await create_file(file=image, upload_path=upload_url) for image in images
        ]
    translation: dict[str, dict[str, str]] = {
        lang.value: {
            "title": data.title,
            "description": data.description,
        }
    }
    stmt = (
        insert(Announcements)
        .values(images=data.files, translations=translation)
        .returning(
            Announcements.uuid,
            Announcements.translations[lang.value]["title"].label("title"),
            Announcements.translations[lang.value]["description"].label("description"),
            Announcements.images,
            Announcements.created_at,
            Announcements.updated_at,
        )
    )
    result = await session.execute(stmt)
    await session.commit()
    return result.one()


async def get_all_announcements(
    session: AsyncSession, lang: Languages = None
) -> Sequence[Row]:
    if lang is None:
        stmt = select(
            Announcements.uuid,
            Announcements.images,
            Announcements.created_at,
            Announcements.updated_at,
            Announcements.translations,
        )
    else:
        stmt = select(
            Announcements.uuid,
            Announcements.images,
            Announcements.translations[lang.value]["title"].label("title"),
            Announcements.translations[lang.value]["description"].label("description"),
            Announcements.created_at,
            Announcements.updated_at,
        ).where(Announcements.translations[lang.value].isnot(None))
    result = await session.execute(stmt)
    result = result.all()
    return result


async def append_images(
    announcement: Row,
    data: UploadImagesToUpdateAnnouncement,
    session: AsyncSession,
) -> Row:
    upload_url = UPLOAD_DIR / date.today().strftime("%Y-%m-%d")
    upload_url.mkdir(parents=True, exist_ok=True)
    files = [
        await create_file(file=image, upload_path=upload_url) for image in data.files
    ]
    images: list = announcement.__getattr__("images")
    images = images + files
    uuid = announcement.__getattr__("uuid")
    stmt = (
        update(Announcements)
        .values(images=images)
        .where(Announcements.uuid == uuid)
        .returning(
            Announcements.uuid,
            Announcements.images,
            Announcements.created_at,
            Announcements.updated_at,
            Announcements.translations,
        )
    )
    result = await session.execute(stmt)
    await session.commit()
    return result.one()


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
