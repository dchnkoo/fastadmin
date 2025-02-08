from contextlib import asynccontextmanager, contextmanager
from typing import Generic, TypeVar

from sqlalchemy import Connection, Engine
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine


class ConnectionMeta(type):
    _instance = None

    def __call__(self, *args, **kwds):
        if self._instance is None:
            self._instance = super().__call__(*args, **kwds)
        return self._instance


_T = TypeVar("_T", AsyncConnection, Connection)
_E = TypeVar("_E", Engine, AsyncEngine)


# TODO: tests
class ConnectionABS(Generic[_T, _E]):
    def __init__(self, engine: _E):
        self.connections: set[_T] = set()
        self.engine = engine

    @property
    def empty(self) -> bool:
        return not self.connections

    def new_connection(self) -> _T:
        conn = self.engine.connect()
        self.add(conn)
        return conn

    def add(self, conn: _T) -> None:
        if conn not in self.connections:
            self.connections.add(conn)

    def get_connection(self) -> _T:
        if self.empty:
            return self.new_connection()

        for conn in self.connections:
            if conn.closed:
                self.connections.remove(conn)
            return conn
        return self.new_connection()

    @contextmanager
    def connection(self):
        conn = self.get_connection()
        try:
            yield conn
        finally:
            if conn.closed:
                self.connections.remove(conn)


class ConnectionRegistry(ConnectionABS[Connection, Engine]):
    def close_all(self):
        for conn in self.connections:
            if not conn.closed:
                conn.close()


class AsyncConnectionRegistry(ConnectionABS[AsyncConnection, AsyncEngine]):
    async def close_all(self):
        for conn in self.connections:
            if not conn.closed:
                await conn.close()


class ConnectionManager(metaclass=ConnectionMeta):
    def __init__(
        self, engine: Engine | None = None, aengine: AsyncEngine | None = None
    ):
        if engine is None and aengine is None:
            raise ValueError("Either engine or aengine must be provided.")

        self.registry = ConnectionRegistry(engine)
        self.async_registry = AsyncConnectionRegistry(aengine)

    @contextmanager
    def connection(self, *, close_after: bool = True, commit: bool = False):
        with self.registry.connection() as conn:
            try:
                yield conn
            except Exception as e:
                if conn.in_transaction():
                    conn.rollback()
                raise e
            else:
                if commit and not conn.in_transaction():
                    conn.commit()
            finally:
                if close_after and not conn.closed:
                    conn.close()

    @asynccontextmanager
    async def aconnection(self, *, close_after: bool = True, commit: bool = False):
        with self.async_registry.connection() as conn:
            try:
                yield conn
            except Exception as e:
                if conn.in_transaction():
                    await conn.rollback()
                raise e
            else:
                if commit and not conn.in_transaction():
                    await conn.commit()
            finally:
                if close_after and not conn.closed:
                    await conn.close()


def connection(func=None, *, close_after: bool = True, commit: bool = False):
    def decorator(func):
        def wrapper(*args, **kwds):
            conn_manager = ConnectionManager()
            with conn_manager.connection(
                close_after=close_after, commit=commit
            ) as conn:
                return func(*args, connection=conn, **kwds)

        return wrapper

    return decorator(func) if callable(func) else decorator


def aconnection(func=None, *, close_after: bool = True, commit: bool = False):
    def decorator(func):
        async def wrapper(*args, **kwds):
            conn_manager = ConnectionManager()
            async with conn_manager.aconnection(
                close_after=close_after, commit=commit
            ) as conn:
                return await func(*args, connection=conn, **kwds)

        return wrapper

    return decorator(func) if func else decorator
