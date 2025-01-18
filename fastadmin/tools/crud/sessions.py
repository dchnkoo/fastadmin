from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    async_sessionmaker,
    async_scoped_session,
    AsyncSession,
)
from sqlalchemy.orm import sessionmaker, scoped_session, Session
from sqlalchemy import Engine

from contextlib import contextmanager

from typing import Generator
import asyncio


class SessionManager:
    def __new__(cls):
        if hasattr(cls, "_instance") is False:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(
        self,
        engine: AsyncEngine | Engine,
        sessionmaker_kwds: dict = ...,
        scoped_session_kwds: dict = ...,
    ):
        self.is_async = isinstance(engine, AsyncEngine)
        self.engine = engine

        sessionmaker_kwds = sessionmaker_kwds or {}
        _sessionmaker = async_sessionmaker if self.is_async else sessionmaker
        self.sessionmaker = _sessionmaker(self.engine, **sessionmaker_kwds)

        scoped_session_kwds = scoped_session_kwds or {}
        _scoped_session = async_scoped_session if self.is_async else scoped_session
        self.scoped_session = _scoped_session(self.sessionmaker, **scoped_session_kwds)

    @contextmanager
    def get(
        self, *, create: bool = False, commit: bool = False
    ) -> Generator[AsyncSession | Session, None, None]:
        if create is True:
            session = self.sessionmaker()
        else:
            session = self.scoped_session()

        try:
            yield session
        except Exception as e:
            if self.is_async:
                asyncio.gather(session.rollback())
            else:
                session.rollback()
            raise e
        else:
            if commit:
                if session.in_transaction() is False:
                    ...

        finally:
            if self.is_async:
                asyncio.gather(session.close())
            else:
                session.rollback()
                session.close()
