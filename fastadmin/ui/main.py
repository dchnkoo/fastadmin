from fastadmin.ui import settings

from fastui import prebuilt_html
import fastapi as fa


main = fa.APIRouter()


@main.get("{path:path}", include_in_schema=False)
def prebuilt() -> fa.responses.HTMLResponse:
    return fa.responses.HTMLResponse(
        prebuilt_html(
            title=settings.PAGE_TITLE,
            api_root_url=settings.API_ROOT_URL,
            api_path_mode=settings.API_PATH_MODE,
            api_path_strip=settings.API_PATH_STRIP,
        )
    )
