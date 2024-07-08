from fastadmin.metadata import FastAdminMeta, MetaInfo
from fastadmin.conf import FastAdminConfig
from fastadmin.utils import types
from fastadmin.ui import urls

from fastui import prebuilt_html, components as c, forms, events as e
import fastapi as fa

from fastui import FastUI, auth as uiauth

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
    if user is not None:
        raise uiauth.AuthRedirect(FastAdminMeta._get_first_home_object_link())

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


@ui.get(urls.SEARCH, response_model=forms.SelectSearchResponse)
async def search_response(
    table: str,
    from_table: str,
    foregin_field: str,
    from_table_field: str,
    q: _t.Optional[str] = None,
    model: _t.Type[FastAdminMeta] = fa.Depends(FastAdminMeta._get_table),
    metainfo: MetaInfo = fa.Depends(FastAdminMeta.__get_metainfo__),
    access: types.AccessCredentials = fa.Depends(
        FastAdminConfig.admin_middleware.get_access_credentials
    ),
):
    session = model.get_session()

    from_table = FastAdminMeta.__get_metainfo__(from_table)

    q = None if q == "" else q

    async with session() as session:
        return await model.selected_search_response(
            session=session,
            foregin_table=metainfo,
            from_table=from_table,
            foregin_field=foregin_field,
            from_table_field=from_table_field,
            q=q,
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


@edit.get(
    urls.EDIT,
    response_model=FastUI,
    response_model_exclude_none=True,
)
async def edit_form_page(
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

    pydantic_model = model.which_model("edit_form")

    async with session() as session:
        return await model.edit_form_page(
            session=session,
            pydantic_model=pydantic_model,
            table_name=table,
            field=field,
            value=value,
            metainfo=metainfo,
            access=access,
        )


@edit.post(urls.UPDATE)
async def edit_data(
    table: str,
    field: str,
    value: str,
    form: _t.AsyncGenerator[type[p.BaseModel], _t.Any] = fa.Depends(
        FastAdminMeta._get_form(edit=True)
    ),
    model: _t.Type[FastAdminMeta] = fa.Depends(FastAdminMeta._get_table),
    metainfo: MetaInfo = fa.Depends(FastAdminMeta.__get_metainfo__),
    access: types.AccessCredentials = fa.Depends(
        FastAdminConfig.admin_middleware.get_access_credentials
    ),
) -> list[c.AnyComponent]:
    async for item in form:
        data = item.model_dump()

        session = model.get_session()

        async with session() as session:
            await model.before_saving(
                session=session,
                signal="edit_form",
                data=data,
                access=access,
                table_name=table,
                model=item,
                field=field,
                value=value,
                metainfo=metainfo,
            )

            meta_field = metainfo.columns.get(field)

            new_data = await model.update(
                session=session,
                where=getattr(model, meta_field.name) == meta_field.python_type(value),
                **data,
            )

            await model.after_saving(
                session=session,
                signal="edit_form",
                data=new_data,
                access=access,
                table_name=table,
                model=item,
                field=field,
                value=value,
                metainfo=metainfo,
            )

        return [c.FireEvent(event=e.BackEvent(), message="Edited!")]


@add.get(
    urls.FORM,
    response_model=FastUI,
    response_model_exclude_none=True,
)
async def form_page(
    table: str,
    model: _t.Type[FastAdminMeta] = fa.Depends(FastAdminMeta._get_table),
    metainfo: MetaInfo = fa.Depends(FastAdminMeta.__get_metainfo__),
    access: types.AccessCredentials = fa.Depends(
        FastAdminConfig.admin_middleware.get_access_credentials
    ),
) -> list[c.AnyComponent]:
    session = model.get_session()

    pydantic_model = model.which_model("form")

    async with session() as session:
        return await model.form_page(
            session=session,
            pydantic_model=pydantic_model,
            table_name=table,
            metainfo=metainfo,
            access=access,
        )


@add.post(urls.FORM_ADD)
async def add_data(
    table: str,
    model: _t.Type[FastAdminMeta] = fa.Depends(FastAdminMeta._get_table),
    form: _t.AsyncGenerator[type[p.BaseModel], _t.Any] = fa.Depends(
        FastAdminMeta._get_form()
    ),
    metainfo: MetaInfo = fa.Depends(FastAdminMeta.__get_metainfo__),
    access: types.AccessCredentials = fa.Depends(
        FastAdminConfig.admin_middleware.get_access_credentials
    ),
) -> list[c.AnyComponent]:
    async for item in form:
        data = item.model_dump()

        session = model.get_session()

        async with session() as session:
            await model.before_saving(
                session=session,
                signal="form",
                data=data,
                access=access,
                table_name=table,
                model=item,
                metainfo=metainfo,
            )

            new_data = await model.insert(session=session, **data)

            await model.after_saving(
                session=session,
                signal="form",
                data=new_data,
                access=access,
                table_name=table,
                model=item,
                metainfo=metainfo,
            )

        return [c.FireEvent(event=e.BackEvent(), message="Added!")]


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
