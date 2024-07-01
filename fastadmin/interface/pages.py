from fastadmin.interface import components as comp
from fastadmin.conf import FastAdminConfig
from fastadmin.utils import types

from fastui import components as c, events as e

from sqlalchemy.ext.asyncio import AsyncSession

import pydantic as p
import typing as _t

if _t.TYPE_CHECKING:
    from fastadmin.metadata import MetaInfo, FastAdminMeta
    from fastadmin.utils.database.asyn import Result


class FastAdminPages(comp.FastAdminComponents):
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
        access: types.AccessCredentials,
    ) -> list[c.AnyComponent]:
        data: "Result" = await cls.get(
            session=session,
            count=True,
            to_dict=True,
        )

        if data.count is None:
            data.count = 1

        return cls.page_frame(
            body=[
                c.Heading(
                    text=cls.__title__ if cls.__title__ else metainfo.table_class_name,
                    level=2,
                    class_name="+ my-2",
                ),
                c.LinkList(
                    links=cls._get_home_links(), mode="tabs", class_name="+ mt-2 mb-4"
                ),
                *cls.table_with_pagination(
                    page=page,
                    data_model=pydantic_model,
                    data=data.data,
                    total=data.count,
                ),
            ],
            heading=[
                *cls.header(
                    title=FastAdminConfig.default_title,
                    title_event=e.GoToEvent(url=cls._get_first_home_object_link()),
                    end_links=[c.Link(components=[c.Text(text=access)])],
                )
            ],
        )

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
