from fastadmin.utils import types

import typing as _t


class FastAdminConfig:
    sql_db_uri: types.URI_WITH_ASYNC_DRIVER
    default_title: str
    api_root_url: str
    api_path_mode: _t.Optional[_t.Literal["append", "query"]]
    api_path_strip: str
