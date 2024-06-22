from fastadmin.model.sqlmodel2pydantic import SQLModel2Pydantic
from fastadmin.model.attributes import ModelAttributes
from fastadmin.model.actions import ModelActions
from fastadmin.model.db_manager import ModelDB

import fastadmin.utils.types as _tb


class FastAdminMeta(
    SQLModel2Pydantic,
    ModelAttributes,
    ModelActions,
    ModelDB,
):
    __metadata__: dict[str, "FastAdminMeta"] = {}

    def __init_subclass__(cls) -> None:
        FastAdminMeta.metadata[cls.__name__] = cls

    @classmethod
    def __get_table___(cls, table: _tb.TableStrName) -> "FastAdminMeta":
        return cls.__metadata__.get(table)
