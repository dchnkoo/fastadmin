from fastadmin.model.sqlmodel2pydantic import SQLModel2Pydantic
from fastadmin.model.attributes import ModelAttributes
from fastadmin.model.actions import ModelActions
from fastadmin.model.db_manager import ModelDB

from fastadmin.interface.pages import FastAdminPages
from fastadmin.conf import FastAdminConfig
import fastadmin.utils.types as _tb

import pydantic as p
import typing as _t

from sqlalchemy.orm import DeclarativeBase
import sqlalchemy as sa


class FastAdminMeta(
    ModelAttributes,
    ModelActions,
    FastAdminPages,
    SQLModel2Pydantic,
    ModelDB,
):
    __metadata__: dict[str, "MetaInfo"] = {}

    def __init_subclass__(cls: type["DeclarativeBase"]) -> None:
        if FastAdminConfig.sqlalchemy_metadata is None:
            for base in cls.__bases__:
                if FastAdminMeta._is_sqlalchemy_base(base):
                    FastAdminConfig.sqlalchemy_metadata = base

        super().__init_subclass__()

        table = cls.__table__

        columns = FastAdminMeta._set_columns(table)

        data = MetaInfo(
            table=cls,
            table_class_name=cls.__name__,
            table_db_name=cls.__tablename__,
            primary_columns={k: v for k, v in columns.items() if v.primary_key},
            foregin_columns={
                k: v for k, v in columns.items() if v.foregin_key is not None
            },
            columns=columns,
        )

        FastAdminMeta.__metadata__[cls.__tablename__] = data

    @classmethod
    def _set_columns(cls, table: "sa.Table") -> dict[str, "TableColumn"]:
        columns = {}

        for column in list(table.columns):
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
        return cls.__metadata__.get(table).table

    @classmethod
    def _get_metainfo(cls, table: _tb.TableStrName) -> "MetaInfo":
        return cls.__metadata__.get(table)

    @classmethod
    def _keys(cls) -> tuple[str]:
        return tuple(cls.__metadata__.keys())

    @classmethod
    def _values(cls) -> tuple["MetaInfo"]:
        return tuple(cls.__metadata__.values())

    @classmethod
    def _items(cls) -> list[tuple[str, "MetaInfo"]]:
        return list(cls.__metadata__.items())

    @classmethod
    def __repr__(cls) -> str:
        if hasattr(cls, "__tablename__"):
            return cls._get_metainfo(cls.__tablename__).__str__()
        return super().__str__(cls)


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
    columns: dict[str, TableColumn]
