from asyncio import current_task

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
    async_scoped_session,
)
from . import settings


class DBActions:
    def __init__(self):
        self.engine = create_async_engine(url=settings.db_url, echo=True)
        self.session_factory = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
            autocommit=False,
        )

    def get_scoped_session(self):
        scoped_session = async_scoped_session(
            session_factory=self.session_factory, scopefunc=current_task
        )
        return scoped_session

    async def session_dependency(self):
        session = self.get_scoped_session()
        try:
            yield session
        finally:
            await session.remove()


db_sessions = DBActions()
