from fastadmin.metadata import FastAdminMeta, MetaInfo
from fastadmin.conf import FastAdminConfig
from fastadmin.utils import types
from fastadmin.ui import urls

from fastui import prebuilt_html, components as c
import fastapi as fa

from fastui import FastUI, forms, auth as uiauth

import pydantic as p
import typing as _t


auth = fa.FastAPI(include_in_schema=False)
uiauth.fastapi_auth_exception_handling(auth)


@auth.post(
    urls.AUTHEFICATE,
    include_in_schema=False,
)
async def autheficate(
    auth: _t.Annotated[
        FastAdminConfig.auth_model, forms.fastui_form(FastAdminConfig.auth_model)
    ],
) -> list[c.AnyComponent]:
    admin = FastAdminMeta._get_admin()

    session = admin.get_session()

    async with session() as session:
        return await admin.authefication(auth_credentials=auth, session=session)


@auth.get(
    urls.AUTHEFICATION,
    response_model=FastUI,
    response_model_exclude_none=True,
    include_in_schema=False,
)
def authefication(
    user: _t.Optional[types.AccessCredentials] = fa.Depends(
        FastAdminConfig.admin_middleware.get_access_credentials_or_none
    ),
):
    # if user is not None:
    #     raise uiauth.AuthRedirect(FastAdminMeta._get_first_home_object_link())

    return [
        c.Navbar(
            title=FastAdminConfig.default_title,
        ),
        c.Page(
            components=[
                c.ModelForm(
                    submit_url=FastAdminConfig.api_root_url + urls.AUTHEFICATE,
                    display_mode="page",
                    model=FastAdminConfig.auth_model,
                )
            ],
            class_name="+ p-2",
        ),
    ]


ui = fa.FastAPI(include_in_schema=False)
ui.add_middleware(FastAdminConfig.admin_middleware)


@ui.post(urls.EXIT)
async def exit(
    user: types.AccessCredentials = fa.Depends(
        FastAdminConfig.admin_middleware.get_access_credentials_or_none
    ),
):
    admin = FastAdminMeta._get_admin()

    session = admin.get_session()

    async with session() as session:
        return await admin.exit(user=user, session=session)


@ui.get(
    urls.HOME,
    response_model=FastUI,
    response_model_exclude_none=True,
)
async def home_page(
    table: str,
    model: _t.Type[FastAdminMeta] = fa.Depends(FastAdminMeta._get_table),
    metainfo: MetaInfo = fa.Depends(FastAdminMeta.__get_metainfo__),
    field: _t.Optional[str] = None,
    search: _t.Optional[str] = None,
    page: int = 1,
    access: types.AccessCredentials = fa.Depends(
        FastAdminConfig.admin_middleware.get_access_credentials
    ),
) -> list[c.AnyComponent]:
    try:
        admin_model: p.BaseModel = model.which_model("admin")

        session = model.get_session()

        async with session() as session:
            return await model.home(
                pydantic_model=admin_model,
                metainfo=metainfo,
                table_name=table,
                session=session,
                search=search,
                access=access,
                field=field,
                page=page,
            )

    except Exception as exc:
        print(exc)
        return [
            c.Error(
                title="Error",
                description=str(exc),
                status_code=fa.status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        ]


@ui.get(
    urls.DETAILS,
    response_model=FastUI,
    response_model_exclude_none=True,
)
async def details_page(
    table: str,
    field: str,
    value: str,
    model: _t.Type[FastAdminMeta] = fa.Depends(FastAdminMeta._get_table),
    metainfo: MetaInfo = fa.Depends(FastAdminMeta.__get_metainfo__),
    access: types.AccessCredentials = fa.Depends(
        FastAdminConfig.admin_middleware.get_access_credentials
    ),
) -> list[c.AnyComponent]:
    session = model.get_session()

    pydantic_model = model.which_model("admin")

    async with session() as session:
        return await model.details(
            session=session,
            pydantic_model=pydantic_model,
            table=table,
            field=field,
            value=value,
            metainfo=metainfo,
            access=access,
        )


add = fa.APIRouter(
    include_in_schema=False,
    dependencies=[
        fa.Depends(
            FastAdminMeta.call_check_permissions_funcion("check_add_permissions")
        )
    ],
)

edit = fa.APIRouter(
    include_in_schema=False,
    dependencies=[
        fa.Depends(
            FastAdminMeta.call_check_permissions_funcion("check_edit_permissions")
        )
    ],
)

delete = fa.APIRouter(
    include_in_schema=False,
    dependencies=[
        fa.Depends(
            FastAdminMeta.call_check_permissions_funcion("check_delete_permissions")
        )
    ],
)


ui.include_router(add)
ui.include_router(edit)
ui.include_router(delete)

main = fa.FastAPI(include_in_schema=False)


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
