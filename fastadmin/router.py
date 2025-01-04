from fastui import AnyComponent, FastUI, prebuilt_html

from .tools import (
    FastAdminTable,
    Template,
    Page,
)

from functools import partial

import fastapi as _fa
import typing as _t

if _t.TYPE_CHECKING:
    import sqlalchemy as _sa


FastAdminMetadata: _t.TypeAlias = "_sa.MetaData"


class FastAdmin(_fa.FastAPI):
    def __init__(
        self,
        metadata: FastAdminMetadata,
        page_meta: type[Page],
        admin_title: str = "FastAdmin",
        root_url: str = "/admin",
        path_mode: _t.Literal["append", "query"] | None = None,
        path_strip: str = "/prebuilt",
        **fastapi_kwds,
    ):
        super(FastAdmin, self).__init__(**fastapi_kwds)

        self.metadata = metadata
        self.__validate_fast_metadata__()

        self.__page_meta__ = page_meta.__pages__

        routes = self.__configure_fast_routes__()
        self.mount(root_url, routes)

        page_meta._tables = metadata.tables

        self._title = admin_title
        self._root_url = root_url
        self._path_mode = path_mode
        self._path_strip = path_strip
        self.__init_prebuilt__()

    def __validate_fast_metadata__(self):
        if (
            all(
                isinstance(table, FastAdminTable)
                for table in self.metadata.tables.values()
            )
            is False
        ):
            raise ValueError("metadata.tables must be FastAdminTable instances")

    def __configure_fast_routes__(self):
        router = _fa.FastAPI()
        for uri, page in self.__page_meta__.items():
            add_route = partial(
                router.add_api_route,
                uri,
                page().render,
                methods=[page.method],
            )
            match page:
                case _ if page._type in (Template, "Template", str):
                    add_route(response_class=_fa.responses.HTMLResponse)
                case _ if page._type in (
                    "list[AnyComponent]",
                    list[AnyComponent],
                    list["AnyComponent"],
                ):
                    add_route(response_model_exclude_none=True, response_model=FastUI)
        return router

    def __init_prebuilt__(self):
        main = _fa.FastAPI()

        @main.get("/{path:path}")
        async def prebuilt() -> _fa.responses.HTMLResponse:
            return _fa.responses.HTMLResponse(
                prebuilt_html(
                    title=self._title,
                    api_root_url=self._root_url,
                    api_path_mode=self._path_mode,
                    api_path_strip=self._path_strip,
                )
            )

        self.mount(self._path_strip, main)
