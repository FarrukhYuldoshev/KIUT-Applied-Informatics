from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    Path,
    HTTPException,
)
from fastapi.responses import FileResponse
from core.settings import db_sessions
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from .schemas import (
    CreateTeacher,
    GetTeachers,
    GetTeachersWithResearchInterests,
    UpdateTeacher,
)
from pathlib import Path as Pathlib
from . import crud
import uuid
from demo_auth import get_active_user
router = APIRouter(prefix="/teachers", tags=["Teachers API"])


@router.post("/", response_model=GetTeachers, status_code=status.HTTP_201_CREATED)
async def create_teacher(
    user = Depends(get_active_user),
    data=Depends(CreateTeacher),
    session: AsyncSession = Depends(db_sessions.session_dependency),
):
    result = await crud.create_teacher(session=session, data=data)
    return result


@router.get("/", response_model=list[GetTeachersWithResearchInterests])
async def get_all_teachers(
    session: AsyncSession = Depends(db_sessions.session_dependency),
):
    result = await crud.get_all_teachers(session=session)
    return result


@router.get("/{teacher_id}", response_model=GetTeachersWithResearchInterests)
async def get_teacher(
    teacher_id: Annotated[uuid.UUID, Path(description="Teacher uuid")],
    session: AsyncSession = Depends(db_sessions.session_dependency),
):
    result = await crud.get_teacher_or_none(teacher_id=teacher_id, session=session)
    return result


@router.patch("/{teacher_id}", response_model=GetTeachersWithResearchInterests)
async def update_teacher(
    teacher_id: Annotated[uuid.UUID, Path(description="Teacher uuid")],
    data: UpdateTeacher = Depends(UpdateTeacher),
    session: AsyncSession = Depends(db_sessions.session_dependency),
    user = Depends(get_active_user),
):
    result = await crud.update_teacher(
        teacher_id=teacher_id, data=data, session=session
    )
    return result


@router.delete("/{teacher_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_teacher(
    teacher_id: uuid.UUID,
    session: AsyncSession = Depends(db_sessions.session_dependency),
    user = Depends(get_active_user),
):
    teacher = await crud.get_teacher_or_none(teacher_id=teacher_id, session=session)
    await crud.delete_teacher(teacher=teacher, session=session)

@router.get("/get-image/")
async def get_image(file_path: str):
    url_file = Pathlib(file_path)
    if url_file.exists() and url_file.is_file():
        return FileResponse(url_file)
    raise HTTPException(status_code = 404, detail="File not found")

# import re
#
# pattern = r"^(?:(\d{4})-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])|(\d{4}))$"
#
# def identify_date_format_and_value(input_str):
#     match = re.match(pattern, input_str)
#     if match:
#         if match.group(1):  # Agar yyyy-mm-dd formati mos kelsa
#             year = match.group(1)
#             month = match.group(2)
#             day = match.group(3)
#             return {"format": "yyyy-mm-dd", "value": f"{year}-{month}-{day}"}
#         elif match.group(4):  # Agar faqat yyyy formati mos kelsa
#             year = match.group(4)
#             return {"format": "yyyy", "value": year}
#     return {"format": "No match", "value": None}  # Mos kelmasa
