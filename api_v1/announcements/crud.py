from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from api_v1.teachers.crud import create_file
from .schemas import CreateAnnouncement
from datetime import date
from pathlib import Path
from core.models import Announcements

UPLOAD_DIR = Path("static/announcements")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


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
