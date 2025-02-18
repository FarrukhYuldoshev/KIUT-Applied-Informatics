from fastapi import APIRouter
from .teachers import router as teacher_router
from .research_interests import router as research_interests_router
from .educations import router as education_router
from .work_experience import router as work_experience_router
from .publications import router as publications_router

router = APIRouter(prefix="/api/v1")
router.include_router(teacher_router)
router.include_router(research_interests_router)
router.include_router(publications_router)
router.include_router(education_router)
router.include_router(work_experience_router)
