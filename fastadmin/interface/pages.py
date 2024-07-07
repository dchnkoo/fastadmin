from fastadmin.interface import components as comp
from fastadmin.conf import FastAdminConfig

from fastui import components as c, events as e

from sqlalchemy.ext.asyncio import AsyncSession

import pydantic as p
import typing as _t

if _t.TYPE_CHECKING:
    from fastadmin.metadata import MetaInfo, FastAdminMeta
    from fastadmin.middleware.jwt import AccessCredetinalsAdmin
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
        access: "AccessCredetinalsAdmin",
    ) -> list[c.AnyComponent]:
        data: "Result" = await cls.get(
            session=session,
            count=True,
            to_dict=True,
        )

        if data.count is None:
            data.count = 0

        body = [
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
        ]

        if await cls.check_add_permissions(
            session=session,
            user=access,
            metainfo=metainfo,
        ):
            body.append(
                c.Button(
                    text="Add",
                    on_click=e.GoToEvent(
                        url=FastAdminConfig.api_path_strip
                        + cls._get_urls().FORM.format(table=table_name)
                    ),
                    html_type="button",
                )
            )

        return cls.page_frame(
            body=body,
            left=cls.exit_event(),
            heading=[
                *cls.header(
                    title=FastAdminConfig.default_title,
                    title_event=e.GoToEvent(url=cls._get_first_home_object_link()),
                    end_links=[c.Link(components=[c.Text(text=access.email)])],
                ),
            ],
        )

    @classmethod
    async def details(
        cls: type["FastAdminMeta"],
        session: AsyncSession,
        pydantic_model: _t.Type[p.BaseModel],
        table: str,
        field: str,
        value: str,
        metainfo: "MetaInfo",
        access: "AccessCredetinalsAdmin",
    ) -> list[c.AnyComponent]:
        detail = await cls.get(
            session=session,
            where=getattr(cls, field) == value,
            all_=False,
            to_dict=True,
        )

        return cls.page_frame(
            heading=[
                *cls.header(
                    title=FastAdminConfig.default_title,
                    title_event=e.GoToEvent(url=cls._get_first_home_object_link()),
                    end_links=[c.Link(components=[c.Text(text=access.email)])],
                ),
            ],
            left=[*cls.exit_event()],
            body=[
                c.Link(components=[c.Text(text="Back")], on_click=e.BackEvent()),
                c.Details(
                    data=pydantic_model(**detail.data),
                ),
            ],
        )

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
