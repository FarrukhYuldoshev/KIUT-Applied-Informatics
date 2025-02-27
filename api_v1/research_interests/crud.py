import uuid
from typing import Annotated, Sequence
from sqlalchemy import select, insert, ScalarResult, update, delete, and_, func, Row
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload, selectinload

from core.models.enumrators import Languages
from core.settings import db_sessions
from core.models import (
    ResearchInterests,
    ResearchInterestsTeacher,
    Teachers,
)
from fastapi import HTTPException, Depends
from starlette import status
from .schemas import (
    CreateResearchInterests,
    ResearchInterestsOnlyUUID,
    GetResearchInterests,
    UpdateResearchInterests,
    GetResearchInterestsWithTeacher,
    DeleteResearchInterests,
    OrderingResearchInterests,
)


async def get_teacher_or_none(
    session: AsyncSession, teacher_id: Annotated[uuid.UUID, ...]
) -> str | None:
    stmt = select(Teachers.uuid).where(Teachers.uuid == teacher_id)
    result = await session.scalar(stmt)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Teacher not found"
        )
    else:
        return result


# async def chech_unique_constraint(title: dict[Languages, dict[str, str]]):
#     stmt = select(ResearchInterests).where(
#         ResearchInterests.translations["uz"]["title"] == title[Languages.uz]["title"],
#         ResearchInterests.translations["ru"]["title"] == title[Languages.uz]["title"],
#         ResearchInterests.translations["en"]["title"] == title[Languages.uz]["title"],
#     )


async def create_research_interests(
    session: AsyncSession,
    data: CreateResearchInterests,
) -> Row:
    stmt = (
        insert(ResearchInterests)
        .values(
            [
                {"translations": {data.lang: {"title": value}}}
                for value in data.title[0].split(",")
            ]
        )
        .returning(
            ResearchInterests.uuid.label("uuid"),
            ResearchInterests.translations[data.lang]["title"].label("title"),
        )
    )
    try:
        result = await session.execute(stmt)
        await session.commit()
    except IntegrityError as e:
        await session.rollback()
        if e.orig.__str__().startswith(
            "<class 'asyncpg.exceptions.UniqueViolationError'>"
        ):
            detail = {
                "code": "unique_violation",
                "message": "The publication(s) were/was already in use.",
                "details": e.params.__str__(),
            }
            raise HTTPException(status.HTTP_409_CONFLICT, detail=detail)
        else:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Database error")
    # stmt = (
    #     insert(ResearchInterests)
    #     .values([item.model_dump() for item in in_r])
    #     .returning(ResearchInterests)
    # )
    # result = await session.scalars(stmt)
    # await session.commit()
    # return result
    return result.all()


async def set_research_interests_to_teacher(
    in_r: ResearchInterestsOnlyUUID,
    session: AsyncSession,
    teacher_id: Annotated[uuid.UUID, ...],
) -> Teachers:
    teacher = await get_teacher_or_none(session=session, teacher_id=teacher_id)
    value = set(uuid4 for uuid4 in in_r.research_interests)
    stmt = select(ResearchInterests).where(ResearchInterests.uuid.in_(value))
    researchs = await session.scalars(stmt)
    existing_uuids = set(item.uuid for item in researchs)
    if missing := value - existing_uuids:
        raise HTTPException(400, f"Invalid UUIDs: {missing}")
    re_t = [
        ResearchInterestsTeacher(teacher_id=teacher, research_interests_id=obj)
        for obj in existing_uuids
    ]
    session.add_all(re_t)
    try:
        await session.commit()
    except IntegrityError as e:
        await session.rollback()
        if e.orig.__str__().startswith(
            "<class 'asyncpg.exceptions.UniqueViolationError'>"
        ):
            detail = {
                "code": "unique_violation",
                "message": "The values already exist",
                "details": e.params.__str__(),
            }
            raise HTTPException(status.HTTP_409_CONFLICT, detail=detail)
        else:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Database error")
    teacher = await get_teacher(session=session, teacher_id=teacher_id)
    return teacher


async def get_all_research_interests(
    session: AsyncSession,
    order_by: OrderingResearchInterests = None,
):
    cte = (
        select(
            ResearchInterests,
            func.count(ResearchInterestsTeacher.research_interests_id).label("count"),
        )
        .join(
            ResearchInterestsTeacher,
            ResearchInterests.uuid == ResearchInterestsTeacher.research_interests_id,
        )
        .group_by(ResearchInterests.uuid)
        .order_by(func.count(ResearchInterestsTeacher.research_interests_id))
        .cte("virtual")
    )
    if order_by is not None:
        if order_by == OrderingResearchInterests.by_title:
            return await session.scalars(
                select(ResearchInterests).order_by(ResearchInterests.title)
            )
        elif order_by == OrderingResearchInterests.by_most_used:
            result = await session.execute(select(cte).order_by(cte.c.count.desc()))
            return result.all()
        else:
            result = await session.execute(
                select(cte).order_by(cte.c.count.desc(), cte.c.title.asc())
            )
            return result.all()
    else:
        stmt = select(ResearchInterests)
        result = await session.scalars(stmt)
        return result


async def get_one_research_interests(
    session: AsyncSession, uuid4: Annotated[uuid.UUID, ...]
) -> ResearchInterests | None:
    stmt = (
        select(ResearchInterests)
        .where(ResearchInterests.uuid == uuid4)
        .options(
            joinedload(ResearchInterests.teachers_viewonly).options(
                selectinload(Teachers.research_interest_viewonly)
            )
        )
    )
    result = await session.scalar(stmt)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Research interest not found"
        )
    else:
        return result


async def update_research_interests(
    uuid4: Annotated[uuid.UUID, ...],
    session: AsyncSession,
    data: UpdateResearchInterests,
) -> ResearchInterests:
    stmt = (
        update(ResearchInterests)
        .where(ResearchInterests.uuid == uuid4)
        .values(title=data.title)
        .returning(ResearchInterests)
    )
    result = await session.scalars(stmt)
    await session.commit()
    return result.one()


async def delete_research_interests_from_selected_teacher(
    session: AsyncSession,
    teacher_id: Annotated[uuid.UUID, ...],
    research_interests: set,
) -> None:

    teacher_uuid = await get_teacher_or_none(session=session, teacher_id=teacher_id)
    stmt = select(ResearchInterestsTeacher.research_interests_id).where(
        and_(
            ResearchInterestsTeacher.research_interests_id.in_(research_interests),
            ResearchInterestsTeacher.teacher_id == teacher_uuid,
        )
    )
    existing_uuids = set(await session.scalars(stmt))
    if missing := research_interests - existing_uuids:
        raise HTTPException(400, f"Invalid UUIDs: {missing}")
    else:
        stmt = delete(ResearchInterestsTeacher).where(
            ResearchInterestsTeacher.research_interests_id.in_(research_interests)
        )
        await session.execute(stmt)
        await session.commit()


async def delete_research_interest(
    uuid4: Annotated[uuid.UUID, ...],
    session: AsyncSession,
) -> None:
    research_interest = await get_one_research_interests(session, uuid4)
    stmt = delete(ResearchInterests).where(
        ResearchInterests.uuid == research_interest.uuid
    )
    await session.execute(stmt)
    await session.commit()


async def get_list_of_research_interests(
    data: list[DeleteResearchInterests],
    session: AsyncSession = Depends(db_sessions.session_dependency),
) -> set:
    values = set(item.uuid for item in data)
    stmt = select(ResearchInterests.uuid).where(ResearchInterests.uuid.in_(values))
    existing_uuids = set(await session.scalars(stmt))
    if missing := values - existing_uuids:
        raise HTTPException(
            status_code=404, detail=f" 404 Not found. Invalid UUIDs: {missing}"
        )
    else:
        return existing_uuids


async def delete_research_interests(
    session: AsyncSession,
    data: set,
) -> None:
    stmt = delete(ResearchInterests).where(ResearchInterests.uuid.in_(data))
    await session.execute(stmt)
    await session.commit()
