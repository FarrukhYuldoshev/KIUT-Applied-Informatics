from fastapi import APIRouter
from .schemas import CreateSubject

router = APIRouter(prefix="/subjects", tags=["Subjects"])


@router.post("/")
async def create_subject(data: CreateSubject):
    print(data)
