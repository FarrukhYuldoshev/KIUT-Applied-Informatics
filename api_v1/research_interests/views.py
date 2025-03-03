from typing import Annotated, Optional, List
from fastapi import Path, Form
from fastapi import (
    APIRouter,
    Depends,
    Query,
)

from core.models.enumrators import Languages
from core.settings import db_sessions
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from .schemas import (
    GetResearchInterests,
    CreateResearchInterests,
    UpdateResearchInterests,
    GetResearchInterestsWithTeacherDetails,
    GetTeacherWithResearchInterests,
    OrderingResearchInterests,
    ResearchInterestsOnlyUUID,
)
from . import crud
from demo_auth import get_active_user
import uuid

router = APIRouter(prefix="/teachers", tags=["Teachers API (research interests)"])


@router.post(
    "/research-interests/",
    response_model=list[GetResearchInterests],
    status_code=status.HTTP_201_CREATED,
    response_model_exclude_unset=True,
)
async def create_research_interests(
    session: Annotated[AsyncSession, Depends(db_sessions.session_dependency)],
    data: CreateResearchInterests = Depends(CreateResearchInterests),
    user=Depends(get_active_user),
):

    result = await crud.create_research_interests(session, data=data)
    return result


@router.post(
    "/research-interests/{teacher_id}",
    response_model=GetTeacherWithResearchInterests,
    response_model_exclude_unset=True,
)
async def set_research_interests_to_teacher(
    data: ResearchInterestsOnlyUUID,
    teacher_id: uuid.UUID,
    session: Annotated[AsyncSession, Depends(db_sessions.session_dependency)],
    user=Depends(get_active_user),
):
    result = await crud.set_research_interests_to_teacher(
        in_r=data, teacher_id=teacher_id, session=session
    )
    return result


@router.get(
    "/research-interests/",
    response_model=list[GetResearchInterests],
    response_model_exclude_unset=True,
    description="Get All Research Interests",
)
async def get_all_research_interests(
    order_by: Annotated[
        OrderingResearchInterests, Query(description="only 3 parametres have")
    ] = None,
    lang: Languages = None,
    session: AsyncSession = Depends(db_sessions.session_dependency),
):
    result = await crud.get_all_research_interests(
        session, order_by=order_by, lang=lang
    )
    print(result)
    return result


@router.get(
    "/research-interests/{uuid4}",
    response_model=GetResearchInterestsWithTeacherDetails,
    response_model_exclude_unset=True,
)
async def get_research_interests(
    uuid4: uuid.UUID,
    lang: Annotated[Languages, Query(description="only 3 parametres have")] = None,
    session: AsyncSession = Depends(db_sessions.session_dependency),
):
    result = await crud.get_one_research_interests(
        uuid4=uuid4, session=session, lang=lang
    )
    return result


@router.patch(
    "/research-interests/{uuid4}",
    response_model=GetResearchInterestsWithTeacherDetails,
    response_model_exclude_unset=True,
)
async def update_research_interests_partial(
    uuid4: Annotated[uuid.UUID, Path(..., description="uuid of research interests")],
    data: UpdateResearchInterests,
    session: AsyncSession = Depends(db_sessions.session_dependency),
    user=Depends(get_active_user),
):
    result = await crud.update_research_interests(
        uuid4=uuid4, session=session, data=data
    )
    return result


@router.delete("/research-interests/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_research_interests(
    teacher_id: Annotated[
        uuid.UUID,
        Query(
            description="Set teacher id if you want delete selected "
            "research interests from teacher otherwise just will "
            "be deleted list of research interests",
        ),
    ] = None,
    data=Depends(crud.get_list_of_research_interests),
    session: AsyncSession = Depends(db_sessions.session_dependency),
    user=Depends(get_active_user),
):
    if teacher_id is None:
        await crud.delete_research_interests(data=data, session=session)
    else:
        await crud.delete_research_interests_from_selected_teacher(
            teacher_id=teacher_id, session=session, research_interests=data
        )
