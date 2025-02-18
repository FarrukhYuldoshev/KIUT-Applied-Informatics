from fastapi import HTTPException, Depends
from sqlalchemy import select, ScalarResult, insert, delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload
from core.settings import db_sessions
from .schemas import CreatePublication, GetPublication, OnlyUUID, UpdatePublication
from core.models import Teachers, PublicationsTeacher, Publications
from uuid import UUID as UUID4
from starlette import status


async def get_teacher_or_none(
    teacher_id: UUID4, session: AsyncSession = Depends(db_sessions.session_dependency)
):
    stmt = select(Teachers.uuid).where(Teachers.uuid == teacher_id)
    teacher = await session.scalar(stmt)
    if teacher is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Teacher not found"
        )
    else:
        return UUID4(str(teacher))


async def get_teacher_with_publications(teacher_id: UUID4, session: AsyncSession):
    stmt = (
        select(Teachers)
        .where(Teachers.uuid == teacher_id)
        .options(joinedload(Teachers.publications_viewonly))
    )
    teacher = await session.scalar(stmt)
    if teacher is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Teacher not found"
        )
    else:
        return teacher


async def create_publication(
    session: AsyncSession, data: CreatePublication
) -> Publications:
    stmt = (
        insert(Publications)
        .values(data.__dict__)
        .returning(Publications)
        .options(selectinload(Publications.teachers_viewonly))
    )
    publication = await session.scalar(stmt)
    await session.commit()
    return publication


async def get_publication(
    publication_id: UUID4,
    session: AsyncSession = Depends(db_sessions.session_dependency),
) -> Publications:
    stmt = (
        select(Publications)
        .options(selectinload(Publications.teachers_viewonly))
        .where(Publications.uuid == publication_id)
    )
    result = await session.scalar(stmt)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="publication is not found"
        )
    else:
        return result


async def get_all_publications(session: AsyncSession):
    stmt = select(Publications).options(selectinload(Publications.teachers_viewonly))
    result = await session.scalars(stmt)
    return result


async def set_publications_to_teacher(
    session: AsyncSession, teacher_id: UUID4, publications: list[OnlyUUID]
):
    publications_ids = set(item.uuid for item in publications)
    stmt = select(Publications.uuid).where(Publications.uuid.in_(publications_ids))
    result = await session.scalars(stmt)
    existing_ids = set(item for item in result)
    if missing := publications_ids - existing_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"missing publications: {missing}",
        )
    else:
        stmt = insert(PublicationsTeacher).values(
            [
                {"teacher_id": teacher_id, "publication_id": value}
                for value in existing_ids
            ]
        )
        try:
            await session.execute(stmt)
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
        teacher = await get_teacher_with_publications(
            teacher_id=teacher_id, session=session
        )
        return teacher


async def update_publication(
    session: AsyncSession,
    data: UpdatePublication,
    publication: Publications,
    partial=False,
):
    for key, value in data.model_dump(exclude_unset=partial).items():
        setattr(publication, key, value)
    try:
        await session.commit()
    except IntegrityError:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Bad request")
    return publication


async def delete_publication(session: AsyncSession, publication: Publications):
    stmt = delete(Publications).where(Publications.uuid == publication.uuid)
    await session.execute(stmt)
    await session.commit()
