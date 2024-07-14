from fastadmin.model.sqlmodel2pydantic import SQLModel2Pydantic
from fastadmin.model.attributes import ModelAttributes
from fastadmin.model.db_manager import ModelDB, Result
from fastadmin.model.actions import ModelActions

from fastadmin.utils.descriptor.clas import classproperty
from fastadmin.utils.func import hash_password
import fastadmin.utils.types as _tb

from fastadmin.interface.pages import FastAdminPages
from fastadmin.conf import FastAdminConfig

from fastadmin.utils.func import patched_fastui_form

from fastui import components as c, events as e

from copy import deepcopy

import fastapi as _fa
import pydantic as p
import typing as _t
import enum

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase
import sqlalchemy as sa


class FastAdminMeta(
    ModelAttributes,
    ModelActions,
    FastAdminPages,
    SQLModel2Pydantic,
    ModelDB,
):
    __admin_metadata: dict[str, "MetaInfo"] = {}

    __sqlalchemy_tables__: list[tuple[type["FastAdminMeta"], sa.Table]] = []

    def __init_subclass__(cls: type["DeclarativeBase"] | type["FastAdminMeta"]) -> None:
        super().__init_subclass__()

        if hasattr(cls, "__table__"):
            FastAdminMeta.__sqlalchemy_tables__.append((cls, cls.__table__))

    @classmethod
    def __realize_meta__(cls) -> None:
        for table_class, table in cls.__sqlalchemy_tables__:
            columns = FastAdminMeta.__meta_set_columns__(table)

            data = MetaInfo(
                table=table_class,
                table_class_name=table_class.__name__,
                table_db_name=table_class.__tablename__,
                table_title=table_class.__title__,
                primary_columns={k: v for k, v in columns.items() if v.primary_key},
                foregin_columns={
                    k: v for k, v in columns.items() if v.foregin_key is not None
                },
                unique_columns={
                    k: v
                    for k, v in columns.items()
                    if v.unique is not None and v.unique is True
                },
                columns=columns,
                permissions=FastAdminMeta._set_permissions(table_class),
                enum_columns={
                    k: v
                    for k, v in columns.items()
                    if issubclass(v.python_type, enum.Enum)
                },
                bool_columns={
                    k: v for k, v in columns.items() if issubclass(v.python_type, bool)
                },
                hide_in_link=table_class.hide_in_link,
            )

            FastAdminMeta.__admin_metadata[table_class.__tablename__] = data

    @classmethod
    def _get_admin(cls) -> type["FastAdminMeta"]:
        return cls._get_table(FastAdminConfig.admin_table_name)

    @classmethod
    def _get_first_home_object_link(cls):
        metainfo: MetaInfo = next(iter(cls.__admin_metadata.values()))

        return cls._get_home_link().format(table=metainfo.table_db_name)

    @classmethod
    def _get_home_links(cls) -> list[c.Link]:
        return [
            c.Link(
                components=[
                    c.Text(text=i.table_title if i.table_title else i.table_class_name)
                ],
                on_click=e.GoToEvent(
                    url=cls._get_home_link().format(table=i.table_db_name)
                ),
                active="startswith:"
                + cls._get_home_link().format(table=i.table_db_name),
            )
            for i in cls.__meta_values__
            if i.hide_in_link is False
        ]

    @classmethod
    def _get_urls(cls):
        from fastadmin.ui import urls

        return urls

    @classmethod
    def _get_home_link(cls) -> str:
        urls = cls._get_urls()

        return FastAdminConfig.api_path_strip + urls.HOME

    @staticmethod
    def _set_permissions(cls: type["FastAdminMeta"]):
        perms = []

        if cls.can_add:
            perms.append("add:" + cls.__name__)

        if cls.can_delete:
            perms.append("delete:" + cls.__name__)

        if cls.can_edit:
            perms.append("edit:" + cls.__name__)

        return perms

    @classproperty
    def _permissions(cls) -> list[str]:
        perms = []

        for perm_list in cls.__meta_values__:
            for perm in perm_list.permissions:
                perms.append(perm)

        return perms

    @classmethod
    def __meta_set_columns__(cls, table: "sa.Table") -> dict[str, "TableColumn"]:
        columns = {}

        for column in table.columns:
            dop_options: dict = column.doc if isinstance(column.doc, dict) else {}

            columns[column.name] = TableColumn(
                name=column.name,
                python_type=column.type.python_type,
                nullable=column.nullable,
                default_value=column.default.arg
                if column.default is not None
                else None,
                unique=column.unique,
                foregin_key=cls._set_foregin_key(column),
                primary_key=column.primary_key,
                column_from_table=table.name,
                options=ColumnOptions(**dop_options),
            )

        return columns

    @staticmethod
    def _is_sqlalchemy_base(cls: object) -> bool:
        return hasattr(cls, "metadata") and issubclass(cls, DeclarativeBase)

    @classmethod
    def _get_form(cls: type["FastAdminMeta"], edit: bool = False):
        async def get_form(
            request: _fa.Request,
            table: type["FastAdminMeta"] = _fa.Depends(cls._get_table),
        ):
            form = table.which_model("form")

            yield patched_fastui_form(form).dependency(request)

        async def get_edit_form(
            request: _fa.Request,
            table: type["FastAdminMeta"] = _fa.Depends(cls._get_table),
        ):
            edit_form = table.which_model("edit_form")

            yield patched_fastui_form(edit_form).dependency(request)

        return get_edit_form if edit else get_form

    @classmethod
    def _set_foregin_key(
        cls,
        column: "sa.Column",
    ) -> _t.Optional["ForeginKey"]:
        foregin_keys = list(column.foreign_keys)

        if foregin_keys:
            foregin_key = foregin_keys[0]

            table, field = foregin_key.target_fullname.split(".", 1)

            return ForeginKey(
                table_name=table,
                field_name=field,
            )

    @classmethod
    def _get_table(cls, table: _tb.TableStrName) -> type["FastAdminMeta"]:
        return deepcopy(cls.__admin_metadata.get(table).table)

    @classmethod
    def __get_metainfo__(cls, table: _tb.TableStrName) -> "MetaInfo":
        return deepcopy(cls.__admin_metadata.get(table))

    @classproperty
    def __meta_keys__(cls) -> tuple[str]:
        return deepcopy(tuple(cls.__admin_metadata.keys()))

    @classproperty
    def __meta_values__(cls) -> tuple["MetaInfo"]:
        return deepcopy(tuple(cls.__admin_metadata.values()))

    @classmethod
    def __meta_items__(cls) -> list[tuple[str, "MetaInfo"]]:
        return deepcopy(list(cls.__admin_metadata.items()))

    @classmethod
    async def authefication(
        cls, auth_credentials: type[p.BaseModel], session: AsyncSession
    ):
        email, password = (
            auth_credentials.email,
            hash_password(auth_credentials.password.get_secret_value()),
        )

        if (
            await cls.exists(
                cls.email == email,
                cls.is_admin.is_(True),
                session=session,
            )
            is False
        ):
            raise _fa.HTTPException(
                status_code=_fa.status.HTTP_404_NOT_FOUND, detail="User doesn't exists."
            )

        user: Result = await cls.get(
            session=session,
            where=(cls.email == email, cls.password == password),
            all_=False,
            count=True,
        )

        user = user.data

        if user is None:
            raise _fa.HTTPException(
                status_code=_fa.status.HTTP_423_LOCKED, detail="Incorrect password."
            )

        response = _fa.responses.JSONResponse(
            content=[
                c.FireEvent(
                    event=e.GoToEvent(url=cls._get_first_home_object_link())
                ).model_dump()
            ]
        )

        await FastAdminConfig.admin_middleware.set_cookies_to_reponse(
            response=response, user=user
        )

        return response

    @classmethod
    async def exit(cls, user: _tb.AccessCredentials, session: AsyncSession):
        response = _fa.responses.JSONResponse(
            content=[
                c.FireEvent(
                    event=e.GoToEvent(
                        url=FastAdminConfig.api_path_strip
                        + cls._get_urls().AUTHEFICATION
                    )
                ).model_dump()
            ]
        )

        FastAdminConfig.admin_middleware.delete_both_cookies_to_response(
            response=response
        )

        return response


class ForeginOptions(p.BaseModel):
    selected_foregin_field: _t.Optional[str] = None


class ColumnOptions(p.BaseModel):
    title: _t.Optional[str] = None
    foregin: _t.Optional[ForeginOptions] = None


class ForeginKey(p.BaseModel):
    table_name: str
    field_name: str


class TableColumn(p.BaseModel):
    name: str
    python_type: type
    nullable: _t.Optional[bool]
    default_value: _t.Optional[_t.Any] = None
    unique: _t.Optional[bool] = None
    primary_key: bool = False
    foregin_key: _t.Optional[ForeginKey] = None
    options: ColumnOptions
    column_from_table: str


class MetaInfo(p.BaseModel):
    table: type[FastAdminMeta]
    table_class_name: str
    table_db_name: str
    table_title: _t.Optional[str]
    primary_columns: dict[str, TableColumn]
    foregin_columns: dict[str, TableColumn] = {}
    unique_columns: dict[str, TableColumn] = {}
    enum_columns: dict[str, TableColumn] = {}
    bool_columns: dict[str, TableColumn] = {}
    columns: dict[str, TableColumn]
    permissions: _t.List[str] = []
    hide_in_link: bool
