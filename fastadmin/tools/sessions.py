from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    async_sessionmaker,
    async_scoped_session,
    AsyncSession,
)
from sqlalchemy.orm import sessionmaker, scoped_session, Session
from sqlalchemy import Engine

from contextlib import contextmanager, asynccontextmanager

from typing import Generator, AsyncGenerator, Callable, TYPE_CHECKING
import asyncio


class SessionManager:
    def __new__(cls, *args, **kwargs):
        if hasattr(cls, "_instance") is False:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(
        self,
        *,
        engine: Engine | None = None,
        aengine: AsyncEngine | None = None,
        sessionmaker_kwds: dict = None,
        scoped_session_kwds: dict = None,
        asessionmaker_kwds: dict = None,
    ):
        if engine is not None:
            self.sessionmaker = sessionmaker[Session](
                engine, **(sessionmaker_kwds or {})
            )
            self.scoped_session = scoped_session(
                self.sessionmaker, **(scoped_session_kwds or {})
            )
        else:
            self.sessionmaker = None
            self.scoped_session = None

        if aengine is not None:
            self.asessionmaker = async_sessionmaker[AsyncSession](
                aengine, **(asessionmaker_kwds or {})
            )
            self.ascoped_session = async_scoped_session(
                self.asessionmaker, scopefunc=asyncio.current_task
            )
        else:
            self.asessionmaker = None
            self.ascoped_session = None

        if self.sessionmaker is None and self.asessionmaker is None:
            raise ValueError("At least one of the engines must be provided")

        self.__class__.__init__ = lambda self, *args, **kw: None

    @contextmanager
    def session(self, commit: bool = False) -> Generator[Session, None, None]:
        if self.sessionmaker is None:
            raise ValueError("SQLAlchemy engine is not provided")

        session = self.scoped_session()
        try:
            yield session
        except Exception as e:
            session.rollback()
            raise e
        else:
            if commit is True and session._trans_context_manager is None:
                session.commit()
        finally:
            if session._trans_context_manager is None:
                self.scoped_session.remove()

    @asynccontextmanager
    async def asession(
        self, commit: bool = False
    ) -> AsyncGenerator[AsyncSession, None]:
        if self.asessionmaker is None:
            raise ValueError("SQLAlchemy async engine is not provided")

        session = self.ascoped_session()

        try:
            yield session
        except Exception as e:
            await session.rollback()
            raise e
        else:
            if commit is True and session.sync_session._trans_context_manager is None:
                await session.commit()
        finally:
            if session.sync_session._trans_context_manager is None:
                await self.ascoped_session.remove()


def session_manager[_F: Callable](func: _F | None = None, *, commit: bool = False):
    def decorator(func: _F) -> _F:
        def wrapper(*args, **kwargs):
            manager = SessionManager()
            with manager.session(commit=commit) as session:
                return func(*args, session=session, **kwargs)

        return wrapper

    return decorator(func) if callable(func) is True else decorator


def asession_manager[_F: Callable](func: _F | None = None, *, commit: bool = False):
    def decorator(func: _F) -> _F:
        async def wrapper(*args, **kwargs):
            manager = SessionManager()
            async with manager.asession(commit=commit) as session:
                return await func(*args, session=session, **kwargs)

        return wrapper

    return decorator(func) if callable(func) is True else decorator


if TYPE_CHECKING:

    def session_manager[_F: Callable](*, commit: bool = False) -> _F: ...
    async def asession_manager[_F: Callable](*, commit: bool = False) -> _F: ...
