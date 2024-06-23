from fastadmin.conf import FastAdminConfig
from fastadmin.utils import types

import fastapi as fa
import typing as _t


class FastAdmin(fa.FastAPI):
    def __init__(
        self,
        sql_db_uri: types.URI_WITH_ASYNC_DRIVER,
        default_title: str = "Admin Panel",
        api_root_url: str = "/api",
        api_path_mode: _t.Optional[_t.Literal["append", "query"]] = None,
        api_path_strip: _t.Optional[str] = None,
        **fastapi_options,
    ) -> None:
        super().__init__(**fastapi_options)

        FastAdminConfig.sql_db_uri = self.sql_db_uri = sql_db_uri
        FastAdminConfig.default_title = self.default_title = default_title
        FastAdminConfig.api_root_url = self.api_root_url = api_root_url
        FastAdminConfig.api_path_mode = self.api_path_mode = api_path_mode
        FastAdminConfig.api_path_strip = self.api_path_strip = api_path_strip

        from fastadmin.ui.main import main

        self.include_router(main)


app = FastAdmin(sql_db_uri="postgresql+asyncpg://test:test@localhost:5432/test")
