from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import Field
from .schemas import Index as IndexSchema, TeachersImage
from core.settings import db_sessions
from . import crud

router = APIRouter(tags=["Home"])


@router.get("/", response_model=IndexSchema)
async def index(
    teachers_image_limit: Annotated[int, Field(default=4, ge=1)] = 4,
    session: AsyncSession = Depends(db_sessions.session_dependency),
):
    result, count = await crud.get_teachers_image(
        session=session, limit=teachers_image_limit
    )
    return IndexSchema(
        teachers=result.all(),
        count=count,
    )
