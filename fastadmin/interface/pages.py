from fastadmin.interface import components as comp
from fastadmin.conf import FastAdminConfig
from fastadmin.utils.func import search_func

from fastui import components as c, events as e

from sqlalchemy.ext.asyncio import AsyncSession

import pydantic as p
import typing as _t

if _t.TYPE_CHECKING:
    from fastadmin.metadata import MetaInfo, FastAdminMeta
    from fastadmin.middleware.jwt import AccessCredetinalsAdmin


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
        enums: dict[str, str],
        bools: dict[str, str],
    ) -> list[c.AnyComponent]:
        data = await search_func(
            session=session,
            metainfo=metainfo,
            field=field,
            search=search,
            enums=enums,
            bools=bools,
            count=True,
            to_dict=True,
        )

        class SearchInput(p.BaseModel):
            search: _t.Optional[str] = p.Field(
                default=None,
                json_schema_extra={
                    "placeholder": "Search..",
                },
                title=FastAdminConfig.words.search,
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
            c.Heading(
                text=FastAdminConfig.words.filter_text, level=4, class_name="+ my-2"
            ),
            c.Div(
                components=[
                    c.Div(
                        components=[
                            *cls.generate_bool_filters(
                                metainfo=metainfo, bool_data=bools
                            )
                        ],
                        class_name="col-sm",
                    ),
                    c.Div(
                        components=[
                            *cls.generate_enum_filters(metainfo=metainfo, enums=enums),
                        ],
                        class_name="col-sm",
                    ),
                    c.Div(
                        components=[
                            c.ModelForm(
                                model=SearchInput,
                                initial={"search": search},
                                method="GOTO",
                                submit_on_change=True,
                                submit_url=".",
                                class_name="d-block",
                                footer=[],
                            ),
                        ],
                        class_name="col-sm",
                    ),
                ],
                class_name="container row align-items-end justify-content-between",
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
                    text=FastAdminConfig.words.add,
                    on_click=e.GoToEvent(
                        url=FastAdminConfig.api_path_strip
                        + cls._get_urls().FORM.format(table=table_name)
                    ),
                    html_type="button",
                )
            )

        return cls.page_frame(
            body=body,
            left=[
                *cls.exit_event(),
            ],
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
        meta_field = metainfo.columns.get(field)

        detail = await cls.get(
            session=session,
            where=getattr(cls, meta_field.name) == meta_field.python_type(value),
            all_=False,
            to_dict=True,
        )

        body = [
            c.Link(
                components=[c.Text(text=FastAdminConfig.words.back)],
                on_click=e.BackEvent(),
            ),
            c.Details(
                data=pydantic_model(**detail.data),
                fields=cls.set_display_lookups_details(
                    metainfo=metainfo, data=detail.data, pydantic_model=pydantic_model
                ),
            ),
        ]

        await cls.set_delete_button(
            session=session,
            metainfo=metainfo,
            access=access,
            body=body,
            table=table,
            field=field,
            value=value,
            delete_url=FastAdminConfig.api_root_url
            + cls._get_urls().DELETE.format(
                table=table,
                field=field,
                value=value,
            ),
        )

        if await cls.check_edit_permissions(
            user=access, session=session, metainfo=metainfo
        ):
            body.append(
                c.Button(
                    text=FastAdminConfig.words.edit,
                    on_click=e.GoToEvent(
                        url=FastAdminConfig.api_path_strip
                        + cls._get_urls().EDIT.format(
                            table=table, field=field, value=value
                        )
                    ),
                    named_style="warning",
                    class_name="+ m-2",
                )
            )

        cls.set_foregin_links_to_details(table=table, detail=detail, body=body)

        return cls.page_frame(
            heading=[
                *cls.header(
                    title=FastAdminConfig.default_title,
                    title_event=e.GoToEvent(url=cls._get_first_home_object_link()),
                    end_links=[c.Link(components=[c.Text(text=access.email)])],
                ),
            ],
            left=[*cls.exit_event()],
            body=body,
        )

    @classmethod
    async def form_page(
        cls: type["FastAdminMeta"],
        session: AsyncSession,
        pydantic_model: _t.Type[p.BaseModel],
        table_name: str,
        metainfo: "MetaInfo",
        access: "AccessCredetinalsAdmin",
    ) -> list[c.AnyComponent]:
        return cls.page_frame(
            body=[
                c.Heading(
                    text=FastAdminConfig.words.form_page_heading
                    % (
                        metainfo.table_title
                        if metainfo.table_title
                        else metainfo.table_class_name,
                    )
                ),
                c.Link(
                    components=[c.Text(text=FastAdminConfig.words.back)],
                    on_click=e.BackEvent(),
                ),
                c.ModelForm(
                    model=pydantic_model,
                    display_mode="page",
                    submit_url=FastAdminConfig.api_root_url
                    + cls._get_urls().FORM_ADD.format(table=table_name),
                ),
            ],
            heading=[
                *cls.header(
                    title=FastAdminConfig.default_title,
                    title_event=e.GoToEvent(url=cls._get_first_home_object_link()),
                    end_links=[c.Link(components=[c.Text(text=access.email)])],
                )
            ],
            left=[*cls.exit_event()],
        )

    @classmethod
    async def edit_form_page(
        cls: type["FastAdminMeta"],
        session: AsyncSession,
        pydantic_model: _t.Type[p.BaseModel],
        table_name: str,
        field: str,
        value: str,
        metainfo: "MetaInfo",
        access: "AccessCredetinalsAdmin",
    ) -> list[c.AnyComponent]:
        meta_field = metainfo.columns.get(field)

        data = await cls.get(
            session=session,
            where=getattr(cls, meta_field.name) == meta_field.python_type(value),
            all_=False,
            to_dict=True,
        )

        await cls.before_edit_view_page(
            session=session,
            table=table_name,
            field=field,
            value=value,
            metainfo=meta_field,
            access=access,
            data=data.data,
        )

        return cls.page_frame(
            body=[
                c.Heading(
                    text=FastAdminConfig.words.edit_page_heading
                    % (
                        metainfo.table_title
                        if metainfo.table_title
                        else metainfo.table_class_name,
                    )
                ),
                c.Link(
                    components=[c.Text(text=FastAdminConfig.words.back)],
                    on_click=e.BackEvent(),
                ),
                c.ModelForm(
                    model=pydantic_model,
                    initial=data.data,
                    display_mode="page",
                    submit_url=FastAdminConfig.api_root_url
                    + cls._get_urls().UPDATE.format(
                        table=table_name, field=field, value=value
                    ),
                ),
            ],
            heading=[
                *cls.header(
                    title=FastAdminConfig.default_title,
                    title_event=e.GoToEvent(url=cls._get_first_home_object_link()),
                    end_links=[c.Link(components=[c.Text(text=access.email)])],
                )
            ],
            left=[*cls.exit_event()],
        )
