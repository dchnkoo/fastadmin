from contextlib import contextmanager

from typing import TypeVar, Generic, Iterable

from sqlalchemy import Engine, Connection
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncConnection


class ConnectionMeta(type):
    _instance = None

    def __call__(self, *args, **kwds):
        if self._instance is None:
            self._instance = super().__call__(*args, **kwds)
        return self._instance


_T = TypeVar("_T", AsyncConnection, Connection)
_E = TypeVar("_E", Engine, AsyncEngine)


class ConnectionSet(set, Generic[_T, _E]):
    def __init__(self, iterable: Iterable[_T], /, engine: _E):
        super(ConnectionSet, self).__init__(iterable)
        self.engine = engine

    @property
    def empty(self) -> bool:
        return len(self) == 0

    def new(self) -> _T:
        return self.engine.connect()

    def get(self) -> _T:
        if self.empty:
            return self.new()

        conn = self.pop()  # noqa F841


class ConnectionABS(Generic[_T, _E]):
    def __init__(self, engine: _E):
        self.connections: ConnectionSet[_T, _E] = ConnectionSet(engine=engine)

    def add(self, conn: _T) -> None:
        self.connections.add(conn)

    @contextmanager
    def connection(self):
        conn = self.connections.get()
        try:
            yield conn
        finally:
            if not conn.closed:
                self.connections.add(conn)


class ConnectionRegistry(ConnectionABS[Connection, Engine]):
    pass


class AsyncConnectionRegistry(ConnectionABS[AsyncConnection, AsyncEngine]):
    pass


class ConnectionManager(metaclass=ConnectionMeta):
    def __init__(
        self, engine: Engine | None = None, aengine: AsyncEngine | None = None
    ):
        if engine is None and aengine is None:
            raise ValueError("Either engine or aengine must be provided.")

        self.registry = ConnectionRegistry(engine)
        self.async_registry = AsyncConnectionRegistry(aengine)
