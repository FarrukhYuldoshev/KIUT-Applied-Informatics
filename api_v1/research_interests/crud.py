import uuid
from typing import Annotated, Sequence, Any, Coroutine
from sqlalchemy import select, insert, ScalarResult, update, delete, and_, func, Row
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload, selectinload

from api_v1.research_interests.schemas import GetResearchInterests
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
    OnlyUUID,
    DeleteResearchInterests,
    OrderingResearchInterests,
)


async def get_teacher_or_none(
    session: AsyncSession, teacher_id: Annotated[uuid.UUID, ...]
) -> Teachers:
    stmt = (
        select(Teachers)
        .options(selectinload(Teachers.research_interest_viewonly))
        .where(Teachers.uuid == teacher_id)
    )
    result = await session.scalar(stmt)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Teacher not found"
        )
    else:
        return result


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
        ResearchInterestsTeacher(teacher=teacher, research_interests_id=obj)
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
    await session.refresh(teacher)
    return teacher


async def get_all_research_interests(
    session: AsyncSession,
    lang: Languages = None,
    order_by: OrderingResearchInterests = None,
):
    research_interests_fields = [ResearchInterests]
    if lang is not None:
        research_interests_fields = [
            ResearchInterests.uuid.label("uuid"),
            ResearchInterests.translations[lang]["title"].label("title"),
        ]
    cte = (
        select(
            *research_interests_fields,
            func.count(ResearchInterestsTeacher.research_interests_id).label(
                "using_count"
            ),
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
            if lang is None:
                stmt = select(*research_interests_fields)
                result = await session.scalars(stmt)
                return result
            else:
                stmt = select(*research_interests_fields).order_by(
                    ResearchInterests.translations[lang]["title"]
                )
                result = await session.execute(stmt)
                return result.all()
        elif order_by == OrderingResearchInterests.by_most_used:
            result = await session.execute(
                select(cte).order_by(cte.c.using_count.desc())
            )
            return result.all()
        else:
            if lang is None:
                result = await session.execute(
                    select(cte).order_by(
                        cte.c.using_count.desc(),
                        cte.c.translations[lang]["title"].asc(),
                    )
                )
            else:
                result = await session.execute(
                    select(cte).order_by(cte.c.using_count.desc(), cte.c.title.asc())
                )
            return result.all()
    else:
        stmt = select(*research_interests_fields)
        if lang is not None:
            result = await session.execute(stmt)
            return result.all()
        else:
            result = await session.scalars(stmt)
            return result


async def get_one_research_interests(
    session: AsyncSession, uuid4: Annotated[uuid.UUID, ...], lang: Languages = None
) -> GetResearchInterests:
    cte = (
        select(
            ResearchInterestsTeacher.research_interests_id,
            func.count(ResearchInterestsTeacher.research_interests_id).label(
                "using_count"
            ),
        )
        .group_by(ResearchInterestsTeacher.research_interests_id)
        .where(ResearchInterestsTeacher.research_interests_id == uuid4)
        .cte("virtual")
    )
    stmt = (
        select(ResearchInterests, cte.c.using_count)
        .where(ResearchInterests.uuid == uuid4)
        .options(selectinload(ResearchInterests.teachers_viewonly))
        .join(
            cte,
            onclause=cte.c.research_interests_id == uuid4,
            isouter=True,
        )
    )
    result = await session.execute(stmt)
    result = result.one_or_none()
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Research interest not found"
        )
    else:
        research: ResearchInterests = result.__getattr__(ResearchInterests)
        using_count = result.__getattr__("using_count")
        data = GetResearchInterests(uuid=research.uuid)
        if lang is not None:
            if research.translations.get(lang) is not None:
                data.title = research.translations[lang].get("title")
        else:
            data.translations = research.translations
        if using_count is not None:
            data.using_count = using_count
            data.teachers_ids = [
                OnlyUUID(uuid=value.uuid) for value in research.teachers_viewonly
            ]
        return data


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


async def get_list_of_research_interests(
    data: list[DeleteResearchInterests],
    session: AsyncSession = Depends(db_sessions.session_dependency),
) -> set:
    values = set(item.uuid for item in data)
    stmt = select(ResearchInterests.uuid).where(ResearchInterests.uuid.in_(values))
    existing_uuids = set(await session.scalars(stmt))
    if missing := values - existing_uuids:
        raise HTTPException(
            status_code=400, detail=f" Bad request! Invalid UUIDs: {missing}"
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
