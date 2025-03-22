import uvicorn
from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

from api_v1 import router as api_router
from demo_auth import jwt_router
from fastapi.middleware.cors import CORSMiddleware
from sqladmin import Admin
from core.settings import db_sessions
from admin import (
    TeachersView,
    ResearchInterestsView,
    PublicationsView,
    EducationView,
    SubjectsView,
    AcademicProgramsView,
    WorkExperienceView,
)
from admin.auth import authentication_backend

app = FastAPI(
    title="Applied Informatics",
    description="API for control web-application",
    version="0.1.0",
    redoc_url=None,
    contact={
        "name": "Farrukh Yuldoshev",
        "email": "codingmaestro.uz@gmail.com",
    },
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
admin = Admin(
    app, engine=db_sessions.engine, authentication_backend=authentication_backend
)
admin.add_view(TeachersView)
admin.add_view(ResearchInterestsView)
admin.add_view(PublicationsView)
admin.add_view(EducationView)
admin.add_view(WorkExperienceView)
admin.add_view(SubjectsView)
admin.add_view(AcademicProgramsView)
app.include_router(api_router)
app.include_router(jwt_router)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        proxy_headers=True,
        forwarded_allow_ips="*",
    )
