import uuid
from typing import Annotated
from sqlalchemy import select, insert, delete, and_, func, Row
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

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
    OrderingResearchInterests,
)


async def get_teacher_or_none(
    session: AsyncSession, teacher_id: Annotated[uuid.UUID, ...]
) -> Teachers:
    stmt = (
        select(Teachers)
        .options(
            selectinload(Teachers.research_interest_viewonly).selectinload(
                ResearchInterests.teachers_viewonly
            )
        )
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
):
    research_interest = ResearchInterests(translations=data.translations)
    session.add(research_interest)
    if data.teachers is not None:
        input_teachers = set(data.teachers)
        stmt = select(Teachers.uuid).where(Teachers.uuid.in_(input_teachers))
        existing_teachers = set(await session.scalars(stmt))
        if missing := input_teachers - existing_teachers:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Bad request missing uuids: missing={missing}",
            )
        else:
            teachers_with_research_interests = [
                ResearchInterestsTeacher(
                    teacher_id=value, research_interest=research_interest
                )
                for value in existing_teachers
            ]
            session.add_all(teachers_with_research_interests)
    try:
        await session.commit()
        await session.scalar(
            select(ResearchInterests)
            .where(ResearchInterests.uuid == research_interest.uuid)
            .options(selectinload(ResearchInterests.teachers_viewonly))
            .limit(1)
        )
    except IntegrityError as e:
        await session.rollback()
        if "UniqueViolationError" in str(e.orig):
            raise HTTPException(
                status_code=409,
                detail=f"Research Interest conflict title:  {e}",
            )
        else:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Database error")
    return research_interest


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
    teacher = await get_teacher_or_none(session=session, teacher_id=teacher.uuid)
    return teacher


async def get_all_research_interests(
    session: AsyncSession,
    lang: Languages,
    order_by: OrderingResearchInterests = None,
):
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
            isouter=True,
        )
        .group_by(ResearchInterests.uuid)
        .order_by(func.count(ResearchInterestsTeacher.research_interests_id))
        .cte("virtual")
    )
    if order_by is not None:
        if order_by == OrderingResearchInterests.by_title:
            stmt = select(*research_interests_fields).order_by(
                ResearchInterests.translations[lang]["title"]
            )
        elif order_by == OrderingResearchInterests.by_most_used:
            stmt = select(cte).order_by(cte.c.using_count.desc())
        else:
            stmt = select(cte).order_by(cte.c.using_count.desc(), cte.c.title.asc())
    else:
        stmt = select(*research_interests_fields)
    result = await session.execute(stmt)
    return result.all()


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
        data = GetResearchInterests(
            uuid=research.uuid, teachers_viewonly=research.teachers_viewonly
        )
        if lang is not None:
            data.title = research.translations.get(lang, {}).get("title")
        else:
            data.translations = research.translations
        if using_count is not None:
            data.using_count = using_count
        else:
            data.using_count = 0
        return data


async def get_research_interests_of_teacher(
    session: AsyncSession, teacher_id: uuid.UUID, lang: Languages = None
):
    cte = (
        select(
            ResearchInterestsTeacher.research_interests_id,
            ResearchInterestsTeacher.teacher_id,
            func.count(ResearchInterestsTeacher.research_interests_id)
            .over(partition_by=ResearchInterestsTeacher.research_interests_id)
            .label("using_count"),
        )
        .join(
            ResearchInterests,
            onclause=ResearchInterestsTeacher.research_interests_id
            == ResearchInterests.uuid,
        )
        .cte("virtual")
    )
    stmt = (
        select(ResearchInterests, cte.c.using_count)
        .options(selectinload(ResearchInterests.teachers_viewonly))
        .join(cte, ResearchInterests.uuid == cte.c.research_interests_id)
        .where(cte.c.teacher_id == teacher_id)
    )
    results = await session.execute(stmt)
    results = results.all()
    data: list[GetResearchInterests] = []
    for result in results:
        research: ResearchInterests = result.__getattr__(ResearchInterests)
        using_count = result.__getattr__("using_count")
        model_research = GetResearchInterests(
            uuid=research.uuid, teachers_viewonly=research.teachers_viewonly
        )
        data.append(model_research)
        if lang is not None:
            model_research.title = research.translations.get(lang, {}).get("title")
        else:
            model_research.translations = research.translations
        if using_count is not None:
            model_research.using_count = using_count
        else:
            model_research.using_count = 0
    return data


async def update_research_interests(
    uuid4: Annotated[uuid.UUID, ...],
    session: AsyncSession,
    data: UpdateResearchInterests,
):
    stmt = (
        select(ResearchInterests)
        .options(
            selectinload(ResearchInterests.teachers),
            selectinload(ResearchInterests.teachers_viewonly),
        )
        .where(ResearchInterests.uuid == uuid4)
    )
    research = await session.scalar(stmt)
    if research is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Research interest not found"
        )
    else:
        if data.teachers is not None:
            await session.execute(
                delete(ResearchInterestsTeacher).where(
                    ResearchInterestsTeacher.research_interests_id == research.uuid
                )
            )
            research_interests_teachers = [
                ResearchInterestsTeacher(
                    teacher_id=value,
                    research_interests_id=research.uuid,
                )
                for value in data.teachers
            ]
            research.teachers = research_interests_teachers
        if data.translations is not None:
            research.translations.update(**data.translations)
        try:
            await session.commit()
        except IntegrityError as e:
            if "UniqueViolationError" in str(e.orig):
                raise HTTPException(
                    status_code=409,
                    detail=f"Research Interest conflict title:  {e}",
                )
            raise HTTPException(status_code=400, detail="Bad request")
        await session.refresh(research)
        return research


async def delete_research_interests_from_selected_teacher(
    session: AsyncSession,
    teacher_id: Annotated[uuid.UUID, ...],
    research_interests: set,
) -> None:

    teacher = await get_teacher_or_none(session=session, teacher_id=teacher_id)
    stmt = select(ResearchInterestsTeacher.research_interests_id).where(
        and_(
            ResearchInterestsTeacher.research_interests_id.in_(research_interests),
            ResearchInterestsTeacher.teacher_id == teacher.uuid,
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
    data: list[OnlyUUID],
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
