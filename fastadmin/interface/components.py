from fastui import components as c, events as e, types, forms
import fastui.class_name as cls_name

from fastadmin.utils.func import search_func
from fastadmin.conf import FastAdminConfig

import starlette.datastructures as starlette

import pydantic as p
import typing as _t
import base64
import pickle
import enum

if _t.TYPE_CHECKING:
    from fastadmin.metadata import FastAdminMeta, MetaInfo
    from fastadmin.middleware.jwt import AccessCredetinalsAdmin
    from fastadmin.utils.database.asyn import Result
    from sqlalchemy.ext.asyncio import AsyncSession


T = _t.TypeVar("T")

field: _t.TypeAlias = str


class Files:
    @classmethod
    async def combine_files(
        cls: type["FastAdminMeta"],
        session: "AsyncSession",
        data: dict,
        field: str,
        value: str,
        metainfo: "MetaInfo",
    ):
        meta_field = metainfo.columns.get(field)

        old_data = (
            await cls.get(
                session=session,
                where=getattr(cls, meta_field.name) == meta_field.python_type(value),
                all_=False,
                to_dict=True,
            )
        ).data

        for key in cls.find_files_in_data(data=data):
            if isinstance(old_data[key], list):
                data[key] = [
                    cls.convert_python_obj_to_file_bytes(item) for item in data[key]
                ]

                old_data[key].extend(data[key])

                data[key] = old_data[key]

            else:
                data[key] = cls.convert_python_obj_to_file_bytes(data[key])

    @classmethod
    def find_files_in_data(
        cls, data: dict[str, T | starlette.UploadFile | list[starlette.UploadFile]]
    ) -> list[field]:
        keys = []

        check_right_file_type: _t.Callable[[starlette.UploadFile]] = lambda file: (  # noqa E731
            content_type := file.content_type
        ).startswith("image") or content_type.startswith("video")

        for key, value in list(data.items()):
            if isinstance((file := value), starlette.UploadFile) and (
                file.size == 0 or check_right_file_type(file) is False
            ):
                del data[key]

                continue

            if isinstance(
                (file := value), starlette.UploadFile
            ) and check_right_file_type(value):
                keys.append(key)

            elif (
                isinstance(value, bytes)
                and isinstance(
                    (file := cls.convert_bytes_file_to_python_obj(value)),
                    starlette.UploadFile,
                )
                and check_right_file_type(file=file)
            ):
                data[key] = file

                keys.append(key)

            elif isinstance(value, list):
                if any(
                    (
                        files := [
                            isinstance(item, starlette.UploadFile)
                            and (item.size == 0 or check_right_file_type(item) is False)
                            for item in value
                        ]
                    )
                ):
                    for index, item in enumerate(files):
                        if item:
                            del value[index]

                            data[key] = value

                    keys.append(key)

                    continue

                if all(
                    isinstance(item, starlette.UploadFile)
                    and check_right_file_type(item)
                    for item in value
                ):
                    keys.append(key)

                elif files := [
                    file
                    for item in value
                    if isinstance(item, bytes)
                    and isinstance(
                        (file := cls.convert_bytes_file_to_python_obj(item)),
                        starlette.UploadFile,
                    )
                    and check_right_file_type(file=file)
                ]:
                    data[key] = files

                    keys.append(key)

        return keys

    @staticmethod
    def convert_bytes_file_to_python_obj(file: bytes, **kw) -> starlette.UploadFile:
        return pickle.loads(file, **kw)

    @staticmethod
    def convert_python_obj_to_file_bytes(file: starlette.UploadFile, **kw) -> bytes:
        return pickle.dumps(file, **kw)

    @classmethod
    async def convert_file_obj_to_bytes(
        cls, data: dict[str, T | starlette.UploadFile | list[starlette.UploadFile]]
    ) -> None:
        for key in cls.find_files_in_data(data=data):
            value = data.get(key)

            if isinstance(value, list):
                data[key] = [
                    cls.convert_python_obj_to_file_bytes(item) for item in value
                ]

            else:
                data[key] = cls.convert_python_obj_to_file_bytes(value)

    @classmethod
    def image_component(
        cls: type["FastAdminMeta"],
        table: str,
        value: str,
        field: str,
        key: str,
        index: _t.Optional[int],
        file: starlette.UploadFile,
    ):
        click_url = FastAdminConfig.api_path_strip + cls._get_urls().FILE_VIEW.format(
            table=table, field=field, value=value, key=key
        )

        return c.Image(
            src=f"data:{file.content_type};base64, {base64.b64encode(file.file.read()).decode("utf-8")}",
            alt=file.filename,
            referrer_policy="same-origin",
            class_name="+ border border-dark",
            loading="lazy",
            on_click=e.GoToEvent(
                url=click_url + f"?index={index}" if index is not None else click_url,
                target="_blank",
            ),
            height=FastAdminConfig.files_height,
            width=FastAdminConfig.files_width,
        )

    @classmethod
    def video_component(
        cls: type["FastAdminMeta"],
        table: str,
        value: str,
        field: str,
        key: str,
        index: _t.Optional[int],
        file: starlette.UploadFile,
    ):
        click_url = FastAdminConfig.api_path_strip + cls._get_urls().FILE_VIEW.format(
            table=table, field=field, value=value, key=key
        )

        return c.Link(
            components=[
                c.Video(
                    sources=[
                        f"data:{file.content_type};base64, {base64.b64encode(file.file.read()).decode("utf-8")}"
                    ],
                    class_name="+ border border-dark",
                    height=FastAdminConfig.files_height,
                    width=FastAdminConfig.files_width,
                )
            ],
            on_click=e.GoToEvent(
                url=click_url + f"?index={index}" if index is not None else click_url,
                target="_blank",
            ),
        )

    @classmethod
    def get_file(
        cls: type["FastAdminMeta"],
        file: starlette.UploadFile,
        table: str,
        field: str,
        value: str,
        key: str,
        index: _t.Optional[int] = None,
    ) -> _t.Union[c.Image, c.Video]:
        content_type = file.content_type

        match content_type:
            case _ if content_type.startswith("image"):
                return cls.image_component(
                    table=table,
                    value=value,
                    field=field,
                    key=key,
                    index=index,
                    file=file,
                )

            case _ if content_type.startswith("video"):
                return cls.video_component(
                    table=table,
                    value=value,
                    field=field,
                    key=key,
                    index=index,
                    file=file,
                )

            case _:
                return c.Error(
                    title="Error", description="This file type is not supported yet."
                )

    @classmethod
    async def file_div(
        cls: type["FastAdminMeta"],
        session: "AsyncSession",
        metainfo: "MetaInfo",
        access: "AccessCredetinalsAdmin",
        file: starlette.UploadFile,
        table: str,
        field: str,
        value: str,
        key: str,
        index: _t.Optional[int] = None,
        delete: bool = False,
    ):
        div_components = [
            cls.get_file(
                file=file,
                index=index,
                table=table,
                field=field,
                value=value,
                key=key,
            )
        ]

        if delete:
            delete_url = FastAdminConfig.api_root_url + cls._get_urls().IMAGE_DELETE

            check_index = index is not None

            await cls.set_delete_button(
                session=session,
                metainfo=metainfo,
                access=access,
                table=table,
                field=field,
                value=value,
                body=div_components,
                delete_url=delete_url + f"?index={index}"
                if check_index
                else delete_url,
                modal_open_trigger_name=f"delete-{index}" if check_index else "delete",
                delete_item_trigger=f"delete-item-{index}"
                if check_index
                else "delete-item",
                key=key,
            )

        return c.Div(components=div_components, class_name="m-5")

    @classmethod
    async def setup_files(
        cls,
        session: "AsyncSession",
        metainfo: "MetaInfo",
        access: "AccessCredetinalsAdmin",
        data: dict[str, _t.Any],
        table: str,
        field: str,
        value: str,
        delete: bool = False,
    ) -> list[c.Div]:
        keys = cls.find_files_in_data(data=data)

        content = []

        args = lambda file, key, index=None: {  # noqa E731
            "session": session,
            "access": access,
            "metainfo": metainfo,
            "file": file,
            "table": table,
            "field": field,
            "value": value,
            "key": key,
            "index": index,
            "delete": delete,
        }

        for key in keys:
            file = data.get(key)

            if isinstance(file, list):
                for index, f in enumerate(file):
                    components = await cls.file_div(**args(f, key, index))

                    content.append(components)

            else:
                components = await cls.file_div(**args(file, key))

                content.append(components)

        return content


class FastAdminComponents(Files):
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
        **format_kw,
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
                                submit_url=delete_url.format(
                                    table=table, field=field, value=value, **format_kw
                                ),
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
                                title=(column.options.title or column.name).title(),
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
                                title=(column.options.title or column.name).title(),
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

    @classmethod
    def download_component(cls: type["FastAdminMeta"], data: dict):
        table = cls.download.get("table")
        field = cls.download.get("field")
        value = cls.download.get("value")(data)
        limit = cls.download.get("limit", 1)

        urls = cls._get_urls()

        metainfo = cls.__get_metainfo__(table=table)

        content = []

        button = c.Button(
            text=FastAdminConfig.words.download_txt
            % ((metainfo.table_title or metainfo.table_db_name).lower(),),
            html_type="button",
            named_style="secondary",
        )

        url = FastAdminConfig.api_root_url + urls.DOWNLOAD_REDIRECT.format(
            table=table, field=field, value=str(value)
        )

        if issubclass(limit.__class__, enum.EnumType):
            button.on_click = e.PageEvent(name="choose-limit")

            Choose = p.create_model("Choose", limit=(limit, ...))

            content.extend(
                [
                    button,
                    c.Modal(
                        title=FastAdminConfig.words.download_title_modal,
                        open_trigger=e.PageEvent(name="choose-limit"),
                        body=[
                            c.ModelForm(
                                submit_on_change=True,
                                submit_url=url,
                                method="GET",
                                model=Choose,
                                footer=[],
                            )
                        ],
                        footer=[
                            c.Button(
                                text=FastAdminConfig.words.cancel,
                                on_click=e.PageEvent(name="choose-limit", clear=True),
                                named_style="secondary",
                            )
                        ],
                    ),
                ]
            )

        else:
            button.on_click = e.PageEvent(name="request-download")

            content.extend(
                [
                    button,
                    c.Form(
                        submit_url=url,
                        submit_trigger=e.PageEvent(name="request-download"),
                        method="GET",
                        form_fields=[
                            c.FormFieldInput(
                                name="limit",
                                title="",
                                html_type="hidden",
                                initial=limit,
                            )
                        ],
                        footer=[],
                    ),
                ]
            )

        return c.Div(components=content, class_name="m-3")
