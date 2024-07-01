from fastadmin.model.sqlmodel2pydantic import SQLModel2Pydantic
from fastadmin.model.attributes import ModelAttributes
from fastadmin.model.actions import ModelActions
from fastadmin.model.db_manager import ModelDB, Result

from fastadmin.utils.descriptor.clas import classproperty
import fastadmin.utils.types as _tb

from fastadmin.interface.pages import FastAdminPages
from fastadmin.conf import FastAdminConfig

from fastui import components as c, events as e

import hashlib as _hash
import fastapi as _fa
import pydantic as p
import typing as _t

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
    __admin_metadata__: dict[str, "MetaInfo"] = {}

    def __init_subclass__(cls: type["DeclarativeBase"] | type["FastAdminMeta"]) -> None:
        super().__init_subclass__()

        table = cls.__table__

        columns = FastAdminMeta.__meta_set_columns__(table)

        data = MetaInfo(
            table=cls,
            table_class_name=cls.__name__,
            table_db_name=cls.__tablename__,
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
            permissions=FastAdminMeta._set_permissions(cls),
        )

        FastAdminMeta.__admin_metadata__[cls.__tablename__] = data

    @classmethod
    def _get_admin(cls) -> type["FastAdminMeta"]:
        return cls._get_table(FastAdminConfig.admin_table_name)

    @classmethod
    def _get_first_home_object_link(cls):
        metainfo: MetaInfo = next(iter(cls.__admin_metadata__.values()))

        return cls._get_home_link().format(table=metainfo.table_db_name)

    @classmethod
    def _get_home_links(cls) -> list[c.Link]:
        return [
            c.Link(
                components=[
                    c.Text(text=cls.__title__ if cls.__title__ else i.table_class_name)
                ],
                on_click=e.GoToEvent(
                    url=cls._get_home_link().format(table=i.table_db_name)
                ),
                active="startswith:"
                + cls._get_home_link().format(table=i.table_db_name),
            )
            for i in cls.__meta_values__
        ]

    @classmethod
    def _get_home_link(cls) -> str:
        from fastadmin.ui.urls import HOME

        return FastAdminConfig.api_path_strip + HOME

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
            columns[column.name] = TableColumn(
                name=column.name,
                python_type=column.type.python_type,
                nullable=column.nullable,
                default_value=column.default.arg
                if column.default is not None
                else None,
                unique=column.unique,
                doc=column.doc,
                foregin_key=cls._set_foregin_key(column),
                primary_key=column.primary_key,
            )

        return columns

    @staticmethod
    def _is_sqlalchemy_base(cls: object) -> bool:
        return hasattr(cls, "metadata") and issubclass(cls, DeclarativeBase)

    @classmethod
    def _set_foregin_key(cls, column: "sa.Column") -> _t.Optional["ForeginKey"]:
        foregin_keys = list(column.foreign_keys)

        if foregin_keys:
            foregin_key = foregin_keys[0]

            table, field = foregin_key.target_fullname.split(".", 1)

            return ForeginKey(table_name=table, field_name=field)

    @classmethod
    def _get_table(cls, table: _tb.TableStrName) -> type["FastAdminMeta"]:
        return cls.__admin_metadata__.get(table).table

    @classmethod
    def __get_metainfo__(cls, table: _tb.TableStrName) -> "MetaInfo":
        return cls.__admin_metadata__.get(table)

    @classproperty
    def __meta_keys__(cls) -> tuple[str]:
        return tuple(cls.__admin_metadata__.keys())

    @classproperty
    def __meta_values__(cls) -> tuple["MetaInfo"]:
        return tuple(cls.__admin_metadata__.values())

    @classmethod
    def __meta_items__(cls) -> list[tuple[str, "MetaInfo"]]:
        return list(cls.__admin_metadata__.items())

    @classmethod
    async def authefication(
        cls, auth_credentials: type[p.BaseModel], session: AsyncSession
    ):
        email, password = (
            auth_credentials.email,
            _hash.sha256(
                auth_credentials.password.get_secret_value().encode()
            ).hexdigest(),
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

        print(user)

        user = user.data

        if user is None:
            raise _fa.HTTPException(
                status_code=_fa.status.HTTP_423_LOCKED, detail="Incorrect password."
            )

        response = _fa.responses.JSONResponse(
            content=[
                c.FireEvent(event=e.GoToEvent(url=cls._get_home_link())).model_dump()
            ]
        )

        await FastAdminConfig.admin_middleware.set_cookies_to_reponse(
            response=response, user=user
        )

        return response


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
    doc: _t.Optional[str] = None


class MetaInfo(p.BaseModel):
    table: type[FastAdminMeta]
    table_class_name: str
    table_db_name: str
    primary_columns: dict[str, TableColumn]
    foregin_columns: dict[str, TableColumn] = {}
    unique_columns: dict[str, TableColumn] = {}
    columns: dict[str, TableColumn]
    permissions: _t.List[str] = []
