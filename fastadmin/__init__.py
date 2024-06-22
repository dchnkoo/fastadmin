from fastadmin import constants as const

import fastapi as fa
import typing as _t
import os


class FastAdmin(fa.FastAPI):
    def __init__(
        self,
        sql_db_uri: str,
        default_title: str = "Admin Panel",
        api_root_url: str = "/api",
        api_path_mode: _t.Optional[_t.Literal["append", "query"]] = None,
        api_path_strip: str | None = None,
        **fastapi_options,
    ) -> None:
        super().__init__(**fastapi_options)

        os.environ[const.DATABASE_URI_KEY] = sql_db_uri
        os.environ[const.DEFAULT_TITLE_PAGE] = default_title
        os.environ[const.API_ROOT_URL] = api_root_url

        if api_path_mode:
            os.environ[const.API_PATH_MODE] = api_path_mode

        if api_path_strip:
            os.environ[const.API_PATH_STRIP] = api_path_strip
