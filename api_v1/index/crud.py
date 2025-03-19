from sqlalchemy import select, case, func
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import Teachers
from core.models.enumrators import Roles


async def get_teachers_image(session: AsyncSession, limit: int = 4):
    role_level_order = case(
        (
            Teachers.translations["en"]["role"].astext
            == Roles.HEAD_OF_DEPARTMENT.get_name("en"),
            Roles.HEAD_OF_DEPARTMENT.level,
        ),
        (
            Teachers.translations["en"]["role"].astext
            == Roles.PROFESSOR.get_name("en"),
            Roles.PROFESSOR.level,
        ),
        (
            Teachers.translations["en"]["role"].astext
            == Roles.ASSOCIATE_PROFESSOR.get_name("en"),
            Roles.ASSOCIATE_PROFESSOR.level,
        ),
        (
            Teachers.translations["en"]["role"].astext
            == Roles.SENIOR_LECTURER.get_name("en"),
            Roles.SENIOR_LECTURER.level,
        ),
        (
            Teachers.translations["en"]["role"].astext == Roles.TEACHER.get_name("en"),
            Roles.TEACHER.level,
        ),
        (
            Teachers.translations["en"]["role"].astext
            == Roles.PROGRAMMER.get_name("en"),
            Roles.PROGRAMMER.level,
        ),
    )
    cte = select(func.count(Teachers.uuid).label("count"))
    count = await session.scalar(cte)
    stmt = select(Teachers).order_by(role_level_order.asc()).limit(limit)
    return await session.scalars(stmt), count
