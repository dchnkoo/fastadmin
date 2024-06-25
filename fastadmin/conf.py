from fastadmin.utils import types

import typing as _t

if _t.TYPE_CHECKING:
    from sqlalchemy.orm import DeclarativeBase


class FastAdminConfig:
    sql_db_uri: types.URI_WITH_ASYNC_DRIVER
    default_title: str
    api_root_url: str
    api_path_mode: _t.Optional[_t.Literal["append", "query"]]
    api_path_strip: str
    sqlalchemy_metadata: type["DeclarativeBase"] = None
