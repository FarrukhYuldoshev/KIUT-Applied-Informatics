from fastapi import APIRouter, HTTPException
from .teachers import router as teacher_router
from .research_interests import router as research_interests_router
from .educations import router as education_router
from .work_experience import router as work_experience_router
from .publications import router as publications_router
from pathlib import Path
from starlette.responses import FileResponse
from .announcements import announcement_router

router = APIRouter(prefix="/api/v1")


# @router.get("/{file_path:path}")
# async def get_file(file_path: str):
#     url_file = Path(file_path)
#     if url_file.exists() and url_file.is_file():
#         return FileResponse(url_file)
#     raise HTTPException(status_code=404, detail="File not found")


router.include_router(announcement_router)
router.include_router(teacher_router)
router.include_router(research_interests_router)
router.include_router(publications_router)
router.include_router(education_router)
router.include_router(work_experience_router)
