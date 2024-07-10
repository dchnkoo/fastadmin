from fastadmin.utils import types

import pydantic as _p
import typing as _t

if _t.TYPE_CHECKING:
    from fastadmin.middleware.jwt import FastAdminJWT
    from sqlalchemy.orm import DeclarativeBase
    from fastadmin.utils.words import AdminWords


SECONDS: _t.TypeAlias = int


class FastAdminConfig:
    sql_db_uri: types.URI_WITH_ASYNC_DRIVER
    default_title: str
    table_size: int

    api_root_url: str
    api_path_mode: _t.Optional[_t.Literal["append", "query"]]
    api_path_strip: str

    admin_table_name: str
    sqlalchemy_metadata: type["DeclarativeBase"] = None
    secret_token: _t.Union[_t.Callable[[], _t.Coroutine[_t.Any, _t.Any, str]], str]

    access_token_life: SECONDS = 900
    refresh_token_life: SECONDS = 2_592_000

    access_token_name: str = "access-token"
    refresh_token_name: str = "refresh-token"

    admin_middleware: type["FastAdminJWT"]

    auth_model: type[_p.BaseModel]

    words: "AdminWords"
