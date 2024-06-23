from fastadmin.interface import components as comp
from fastui import components as c

from sqlalchemy.ext.asyncio import AsyncSession

import typing as _t


pages = _t.TypeVar("pages", bound="FastAdminPages")


class FastAdminPages(comp.FastAdminComponents):
    @classmethod
    async def home(
        cls,
        table_name: str,
        session: AsyncSession,
        pydantic_model: _t.Type[pages],
        field: _t.Optional[str],
        search: _t.Optional[str],
        page: int,
    ) -> list[c.AnyComponent]:
        ...

    @classmethod
    async def details(
        cls, session: AsyncSession, pydantic_model: _t.Type[pages]
    ) -> list[c.AnyComponent]:
        ...

    @classmethod
    async def form(
        cls, session: AsyncSession, pydantic_model: _t.Type[pages]
    ) -> list[c.AnyComponent]:
        ...

    @classmethod
    async def edit_form(
        cls, session: AsyncSession, pydantic_model: _t.Type[pages]
    ) -> list[c.AnyComponent]:
        ...
