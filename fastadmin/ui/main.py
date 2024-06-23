from fastadmin.metadata import FastAdminMeta
from fastadmin.conf import FastAdminConfig
from fastadmin.ui import urls

from fastui import prebuilt_html, components as c
import fastapi as fa

from fastui import FastUI

import pydantic as p
import typing as _t


ui = fa.APIRouter(prefix=FastAdminConfig.api_root_url)


@ui.get(urls.HOME, response_model=FastUI, response_model_exclude_none=True)
async def home_page(
    table: str,
    model: _t.Type[FastAdminMeta] = fa.Depends(FastAdminMeta.__get_table___),
    field: _t.Optional[str] = None,
    search: _t.Optional[str] = None,
    page: int = 1,
) -> list[c.AnyComponent]:
    try:
        admin_model: p.BaseModel = model.which_model("admin")

        session = model.get_session()

        async with session() as session:
            return await model.home(
                table_name=table,
                session=session,
                pydantic_model=admin_model,
                field=field,
                search=search,
                page=page,
            )

    except Exception as exc:
        return [
            c.Error(
                title="Error",
                description=exc,
                status_code=fa.status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        ]


main = fa.APIRouter()
main.include_router(ui)


@main.get("/{path:path}")
def prebuilt() -> fa.responses.HTMLResponse:
    return fa.responses.HTMLResponse(
        prebuilt_html(
            title=FastAdminConfig.default_title,
            api_root_url=FastAdminConfig.api_root_url,
            api_path_mode=FastAdminConfig.api_path_mode,
            api_path_strip=FastAdminConfig.api_path_strip,
        )
    )
