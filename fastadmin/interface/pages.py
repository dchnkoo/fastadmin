from fastadmin.interface import components as comp

from fastui import components as c

from sqlalchemy.ext.asyncio import AsyncSession

import pydantic as p
import typing as _t

if _t.TYPE_CHECKING:
    from fastadmin.metadata import MetaInfo, FastAdminMeta


class FastAdminPages(comp.FastAdminComponents):
    @classmethod
    def auth(cls: type["FastAdminMeta"]) -> list[c.AnyComponent]:
        ...

    @classmethod
    async def home(
        cls: type["FastAdminMeta"],
        table_name: str,
        metainfo: "MetaInfo",
        session: AsyncSession,
        pydantic_model: _t.Type[p.BaseModel],
        field: _t.Optional[str],
        search: _t.Optional[str],
        page: int,
    ) -> list[c.AnyComponent]:
        ...

    @classmethod
    async def details(
        cls, session: AsyncSession, pydantic_model: _t.Type[p.BaseModel]
    ) -> list[c.AnyComponent]:
        ...

    @classmethod
    async def form_page(
        cls, session: AsyncSession, pydantic_model: _t.Type[p.BaseModel]
    ) -> list[c.AnyComponent]:
        ...

    @classmethod
    async def edit_form_page(
        cls, session: AsyncSession, pydantic_model: _t.Type[p.BaseModel]
    ) -> list[c.AnyComponent]:
        ...
