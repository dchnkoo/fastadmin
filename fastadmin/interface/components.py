from fastui import components as c, events as e, types, forms
import fastui.class_name as cls_name

from fastadmin.utils.func import search_func
from fastadmin.conf import FastAdminConfig

import pydantic as p
import typing as _t

if _t.TYPE_CHECKING:
    from fastadmin.metadata import FastAdminMeta, MetaInfo
    from fastadmin.middleware.jwt import AccessCredetinalsAdmin
    from fastadmin.utils.database.asyn import Result
    from sqlalchemy.ext.asyncio import AsyncSession


class FastAdminComponents:
    @classmethod
    def page_frame(
        cls,
        body: _t.List[c.AnyComponent],
        heading: _t.List[c.AnyComponent] = [],
        left: _t.List[c.AnyComponent] = [],
        right: _t.List[c.AnyComponent] = [],
        footer: _t.List[c.AnyComponent] = [],
    ) -> list[c.AnyComponent]:
        return [
            *heading,
            c.Div(
                components=[
                    *left,
                    c.Page(components=body),
                    *right,
                ],
            ),
            *footer,
        ]

    @classmethod
    def header(
        cls: type["FastAdminMeta"],
        title: _t.Optional[str] = None,
        title_event: _t.Optional[e.AnyEvent] = None,
        start_links: _t.List[c.Link] = [],
        end_links: _t.List[c.Link] = [],
        class_name: cls_name.ClassNameField = None,
    ) -> list[c.AnyComponent]:
        end_links.append(
            c.Link(
                components=[
                    c.Button(
                        text=FastAdminConfig.words.logout,
                        on_click=e.PageEvent(name="exit"),
                        class_name="btn btn-light",
                        html_type="button",
                    )
                ],
            )
        )

        return [
            c.Navbar(
                title=title,
                title_event=title_event,
                start_links=start_links,
                end_links=end_links,
                class_name=class_name,
            )
        ]

    @classmethod
    def exit_event(cls: type["FastAdminMeta"]) -> list[c.AnyComponent]:
        return [
            c.Modal(
                title=FastAdminConfig.words.logout,
                body=[c.Text(text=FastAdminConfig.words.logout_question)],
                open_trigger=e.PageEvent(name="exit"),
                footer=[
                    c.Button(
                        text=FastAdminConfig.words.cancel,
                        on_click=e.PageEvent(name="exit", clear=True),
                        named_style="secondary",
                    ),
                    c.Button(
                        text=FastAdminConfig.words.logout,
                        on_click=e.PageEvent(name="logout"),
                        class_name="btn btn-danger",
                    ),
                ],
            ),
            c.Form(
                submit_url=FastAdminConfig.api_root_url + cls._get_urls().EXIT,
                footer=[],
                submit_trigger=e.PageEvent(name="logout"),
                form_fields=[
                    c.FormFieldInput(
                        name="", title="", initial="data", html_type="hidden"
                    )
                ],
                class_name="",
            ),
        ]

    @classmethod
    def table_with_pagination(
        cls: type["FastAdminMeta"],
        page: int,
        total: int,
        data: _t.Sequence[p.SerializeAsAny[types.DataModel]],
        data_model: _t.Optional[type[p.BaseModel]] = None,
        class_name_table: c._class_name.ClassNameField = None,
        page_query_param: str = "page",
        class_name_pagination: c._class_name.ClassNameField = None,
    ) -> tuple[c.Table, c.Pagination]:
        return [
            c.Table(
                data=[data_model(**i) for i in data] if data_model else data,
                columns=cls.display_lookups,
                data_model=data_model,
                no_data_message=cls.no_data_message,
                class_name=class_name_table,
            ),
            c.Pagination(
                page=page,
                page_size=cls.table_size,
                total=total,
                page_query_param=page_query_param,
                class_name=class_name_pagination,
            ),
        ]

    @classmethod
    def set_foregin_links_to_details(
        cls: type["FastAdminMeta"],
        table: str,
        detail: "Result",
        body: list[c.AnyComponent],
    ):
        components = [
            c.Heading(
                text=FastAdminConfig.words.additional_information,
                level=4,
                class_name="+ mt-2",
            ),
        ]

        for info in cls.__meta_values__:
            for foregin in info.foregin_columns.values():
                if table == foregin.foregin_key.table_name:
                    components.append(
                        c.Button(
                            text=(
                                info.table_title
                                if info.table_title
                                else info.table_class_name
                            ),
                            on_click=e.GoToEvent(
                                url=FastAdminConfig.api_path_strip
                                + cls._get_urls().HOME.format(table=info.table_db_name)
                                + f"?field={foregin.name}&search={str(detail.data.get(foregin.foregin_key.field_name))}",
                                target="_blank",
                            ),
                            class_name="btn btn-outline-success m-2",
                        )
                    )

        if len(components) > 1:
            body.extend(components)

    @classmethod
    def set_display_lookups_details(
        cls: type["FastAdminMeta"],
        metainfo: "MetaInfo",
        pydantic_model: type[p.BaseModel],
        data: dict,
    ) -> list[c.display.DisplayLookup]:
        lookups = []

        list_keys = tuple(metainfo.columns.keys())

        for column_name in pydantic_model.__fields__.keys():
            meta_field = metainfo.columns.get(column_name)
            index = list_keys.index(column_name)

            if column_name in metainfo.foregin_columns:
                lookup = c.display.DisplayLookup(
                    field=meta_field.name,
                    on_click=e.GoToEvent(
                        url=FastAdminConfig.api_path_strip
                        + cls._get_urls().DETAILS.format(
                            table=meta_field.foregin_key.table_name,
                            field=meta_field.foregin_key.field_name,
                            value=data.get(meta_field.name),
                        ),
                        target="_blank",
                    ),
                )

                lookups.insert(index, lookup)

            else:
                lookups.insert(index, c.display.DisplayLookup(field=meta_field.name))

        return lookups

    @classmethod
    async def selected_search_response(
        cls: type["FastAdminMeta"],
        session: "AsyncSession",
        foregin_table: "MetaInfo",
        from_table: "MetaInfo",
        foregin_field: str,
        from_table_field: str,
        access: "AccessCredetinalsAdmin",
        q: _t.Optional[str],
    ) -> forms.SelectSearchResponse:
        options = []

        meta_from_field = from_table.foregin_columns.get(from_table_field)

        result = await search_func(
            session=session,
            metainfo=foregin_table,
            field=meta_from_field.options.foregin.selected_foregin_field,
            search=q,
            ilike=True,
        )

        [
            options.append(
                {
                    "value": str(getattr(i, foregin_field)),
                    "label": str(
                        getattr(
                            i, meta_from_field.options.foregin.selected_foregin_field
                        )
                    ),
                }
            )
            for i in result.data
        ]

        return forms.SelectSearchResponse(options=options)

    @classmethod
    async def set_delete_button(
        cls: type["FastAdminMeta"],
        session: "AsyncSession",
        metainfo: "MetaInfo",
        access: "AccessCredetinalsAdmin",
        body: list[c.AnyComponent],
        table: str,
        field: str,
        value: str,
        delete_url: str,
        modal_open_trigger_name: str = "delete",
        delete_item_trigger: str = "delete-item",
    ):
        if await cls.check_delete_permissions(
            user=access, session=session, metainfo=metainfo
        ):
            body.extend(
                [
                    c.Button(
                        text=FastAdminConfig.words.delete,
                        on_click=e.PageEvent(name=modal_open_trigger_name),
                        class_name="btn btn-danger m-2",
                        html_type="button",
                    ),
                    c.Modal(
                        title=FastAdminConfig.words.confirm_operation,
                        body=[
                            c.Text(
                                text=FastAdminConfig.words.operation_delete_question.format(
                                    field=field, value=value, table=table
                                )
                            ),
                            c.Form(
                                submit_url=delete_url,
                                footer=[],
                                submit_trigger=e.PageEvent(name=delete_item_trigger),
                                form_fields=[
                                    c.FormFieldInput(
                                        name="",
                                        title="",
                                        html_type="hidden",
                                        initial="data",
                                    )
                                ],
                            ),
                        ],
                        open_trigger=e.PageEvent(name=modal_open_trigger_name),
                        footer=[
                            c.Button(
                                text=FastAdminConfig.words.cancel,
                                on_click=e.PageEvent(
                                    name=modal_open_trigger_name, clear=True
                                ),
                                html_type="button",
                                named_style="secondary",
                            ),
                            c.Button(
                                text=FastAdminConfig.words.delete,
                                on_click=e.PageEvent(name=delete_item_trigger),
                                html_type="button",
                                class_name="btn btn-danger",
                            ),
                        ],
                    ),
                ]
            )

    @classmethod
    def generate_enum_filters(
        cls, metainfo: "MetaInfo", enums: dict[str, str]
    ) -> list[c.ModelForm]:
        filters = []

        if metainfo.enum_columns:
            for name, column in metainfo.enum_columns.items():
                value = enums.get(name, None)
                model_name = "enum_" + name

                model = p.create_model(
                    model_name,
                    **{
                        model_name: (
                            _t.Optional[column.python_type],
                            p.Field(
                                default=value,
                                title=column.options.title
                                if column.options.title
                                else column.name.title(),
                            ),
                        )
                    },
                )

                filters.extend(
                    [
                        c.ModelForm(
                            submit_on_change=True,
                            submit_url=".",
                            method="GOTO",
                            model=model,
                            class_name="d-block",
                            initial={model_name: value},
                            footer=[],
                        )
                    ]
                )

        return filters

    @classmethod
    def generate_bool_filters(
        cls, metainfo: "MetaInfo", bool_data: dict[str, str]
    ) -> list[c.ModelForm]:
        filters = []

        if metainfo.bool_columns:
            for name, column in metainfo.bool_columns.items():
                value = bool_data.get(name, None)
                model_name = "bool_" + name

                model = p.create_model(
                    model_name,
                    **{
                        model_name: (
                            _t.Optional[column.python_type],
                            p.Field(
                                default=value,
                                title=column.options.title
                                if column.options.title
                                else column.name.title(),
                                json_schema_extra={"mode": "switch"},
                            ),
                        )
                    },
                )

                filters.extend(
                    [
                        c.ModelForm(
                            submit_on_change=True,
                            submit_url=".",
                            method="GOTO",
                            model=model,
                            class_name="d-block",
                            initial={model_name: value},
                            footer=[],
                        )
                    ]
                )

        return filters
