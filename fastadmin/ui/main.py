from fastadmin.metadata import FastAdminMeta, MetaInfo
from fastadmin.conf import FastAdminConfig
from fastadmin.utils import types
from fastadmin.ui import urls

from fastui import prebuilt_html, components as c, forms, events as e
import fastapi as fa

from fastui import FastUI, auth as uiauth

import pydantic as p
import typing as _t
import copy


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
    request: fa.Request,
) -> list[c.AnyComponent]:
    admin = FastAdminMeta._get_admin()

    session = admin.get_session()

    async with session() as session:
        return await admin.authefication(
            auth_credentials=auth, session=session, request=request
        )


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
    request: fa.Request,
    user: types.AccessCredentials = fa.Depends(
        FastAdminConfig.admin_middleware.get_access_credentials_or_none
    ),
):
    admin = FastAdminMeta._get_admin()

    session = admin.get_session()

    async with session() as session:
        return await admin.exit(user=user, session=session, request=request)


@ui.get(
    urls.HOME,
    response_model=FastUI,
    response_model_exclude_none=True,
)
async def home_page(
    table: str,
    request: fa.Request,
    model: _t.Type[FastAdminMeta] = fa.Depends(FastAdminMeta._get_table),
    metainfo: MetaInfo = fa.Depends(FastAdminMeta.__get_metainfo__),
    field: _t.Optional[str] = None,
    search: _t.Optional[str] = None,
    page: int = 1,
    access: types.AccessCredentials = fa.Depends(
        FastAdminConfig.admin_middleware.get_access_credentials
    ),
    enums: dict[str, str] = fa.Depends(
        FastAdminMeta.get_params_values_with_prefix("enum_")
    ),
    bools: dict[str, str] = fa.Depends(
        FastAdminMeta.get_params_values_with_prefix("bool_")
    ),
) -> list[c.AnyComponent]:
    admin_model: p.BaseModel = model._trash

    session = model.get_session()

    async with session() as session:
        return await model.home(
            pydantic_model=admin_model,
            metainfo=metainfo,
            request=request,
            table_name=table,
            session=session,
            search=search,
            access=access,
            field=field,
            page=page,
            enums=enums,
            bools=bools,
        )


@ui.get(
    urls.DETAILS,
    response_model=FastUI,
    response_model_exclude_none=True,
)
async def details_page(
    table: str,
    field: str,
    value: str,
    request: fa.Request,
    model: _t.Type[FastAdminMeta] = fa.Depends(FastAdminMeta._get_table),
    metainfo: MetaInfo = fa.Depends(FastAdminMeta.__get_metainfo__),
    access: types.AccessCredentials = fa.Depends(
        FastAdminConfig.admin_middleware.get_access_credentials
    ),
) -> list[c.AnyComponent]:
    session = model.get_session()

    pydantic_model = model._admin

    async with session() as session:
        return await model.details(
            session=session,
            pydantic_model=pydantic_model,
            table=table,
            request=request,
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
    request: fa.Request,
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
            request=request,
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
    request: fa.Request,
    model: _t.Type[FastAdminMeta] = fa.Depends(FastAdminMeta._get_table),
    metainfo: MetaInfo = fa.Depends(FastAdminMeta.__get_metainfo__),
    access: types.AccessCredentials = fa.Depends(
        FastAdminConfig.admin_middleware.get_access_credentials
    ),
) -> list[c.AnyComponent]:
    session = model.get_session()

    pydantic_model = model._edit_form

    async with session() as session:
        return await model.edit_form_page(
            session=session,
            pydantic_model=pydantic_model,
            table_name=table,
            request=request,
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
    request: fa.Request,
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
            try:
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
                    request=request,
                )

                meta_field = metainfo.columns.get(field)

                old_data = (
                    await model.get(
                        session=session,
                        where=getattr(model, meta_field.name)
                        == meta_field.python_type(value),
                        all_=False,
                    )
                ).data

                old_data = copy.deepcopy(old_data)

                await model.update(
                    session=session,
                    where=getattr(model, meta_field.name)
                    == meta_field.python_type(value),
                    **data,
                )

                await model.after_saving(
                    session=session,
                    signal="edit_form",
                    data=old_data,
                    access=access,
                    table_name=table,
                    model=item,
                    field=field,
                    value=value,
                    metainfo=metainfo,
                    request=request,
                )

            except Exception as exc:
                raise fa.HTTPException(
                    status_code=fa.status.HTTP_400_BAD_REQUEST, detail=str(exc)
                )

        return [c.FireEvent(event=e.BackEvent(), message="Edited!")]


@add.get(
    urls.FORM,
    response_model=FastUI,
    response_model_exclude_none=True,
)
async def form_page(
    table: str,
    request: fa.Request,
    model: _t.Type[FastAdminMeta] = fa.Depends(FastAdminMeta._get_table),
    metainfo: MetaInfo = fa.Depends(FastAdminMeta.__get_metainfo__),
    access: types.AccessCredentials = fa.Depends(
        FastAdminConfig.admin_middleware.get_access_credentials
    ),
) -> list[c.AnyComponent]:
    session = model.get_session()

    pydantic_model = model._form

    async with session() as session:
        return await model.form_page(
            session=session,
            pydantic_model=pydantic_model,
            table_name=table,
            metainfo=metainfo,
            access=access,
            request=request,
        )


@add.post(urls.FORM_ADD)
async def add_data(
    table: str,
    request: fa.Request,
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
            try:
                await model.before_saving(
                    session=session,
                    signal="form",
                    data=data,
                    access=access,
                    table_name=table,
                    model=item,
                    metainfo=metainfo,
                    request=request,
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
                    request=request,
                )

            except Exception as exc:
                raise fa.HTTPException(
                    status_code=fa.status.HTTP_400_BAD_REQUEST, detail=str(exc)
                )

        return [c.FireEvent(event=e.BackEvent(), message="Added!")]


@delete.post(urls.DELETE)
async def delete_item(
    table: str,
    field: str,
    value: str,
    request: fa.Request,
    model: _t.Type[FastAdminMeta] = fa.Depends(FastAdminMeta._get_table),
    metainfo: MetaInfo = fa.Depends(FastAdminMeta.__get_metainfo__),
    access: types.AccessCredentials = fa.Depends(
        FastAdminConfig.admin_middleware.get_access_credentials
    ),
):
    session = model.get_session()

    meta_field = metainfo.columns.get(field)

    async with session() as session:
        where = getattr(model, meta_field.name) == meta_field.python_type(value)

        data = (
            await model.get(session=session, where=where, all_=False, to_dict=True)
        ).data

        try:
            await model.before_delete(
                table=table,
                field=field,
                value=value,
                metainfo=metainfo,
                access=access,
                data=data,
                request=request,
            )

            await model.delete(session=session, where=where)

            await model.after_delete(
                session=session,
                table=table,
                field=field,
                value=value,
                metainfo=metainfo,
                access=access,
                data=data,
                request=request,
            )

        except Exception as exc:
            raise fa.HTTPException(
                status_code=fa.status.HTTP_400_BAD_REQUEST, detail=str(exc)
            )

    return [c.FireEvent(event=e.BackEvent(), message="Deleted!")]


@delete.post(urls.IMAGE_DELETE)
async def delete_image(
    table: str,
    field: str,
    value: str,
    key: str,
    index: _t.Optional[int] = None,
    model: type[FastAdminMeta] = fa.Depends(FastAdminMeta._get_table),
    metainfo: MetaInfo = fa.Depends(FastAdminMeta.__get_metainfo__),
    access: types.AccessCredentials = fa.Depends(
        FastAdminConfig.admin_middleware.get_access_credentials
    ),
):
    session = model.get_session()

    async with session() as session:
        meta_field = metainfo.columns.get(field)
        where = getattr(model, meta_field.name) == meta_field.python_type(value)

        image = (
            await model.get(
                session=session,
                where=where,
                table=(getattr(model, key),),
                all_=False,
            )
        ).data

        if index is not None:
            del image[index]

        else:
            image = None

        await model.update(session=session, where=where, **{key: image})

    return [c.FireEvent(event=e.BackEvent())]


ui.include_router(add)
ui.include_router(edit)
ui.include_router(delete)


@ui.get(urls.FILE_VIEW, response_model=FastUI, response_model_exclude_none=True)
async def get_file(
    table: str,
    field: str,
    value: str,
    key: str,
    request: fa.Request,
    index: _t.Optional[int] = None,
    model: type[FastAdminMeta] = fa.Depends(FastAdminMeta._get_table),
    metainfo: MetaInfo = fa.Depends(FastAdminMeta.__get_metainfo__),
    access: types.AccessCredentials = fa.Depends(
        FastAdminConfig.admin_middleware.get_access_credentials
    ),
):
    session = model.get_session()

    async with session() as session:
        return await model.image_page(
            request=request,
            session=session,
            table=table,
            field=field,
            value=value,
            key=key,
            index=index,
            metainfo=metainfo,
            access=access,
        )


@ui.get(urls.DOWNLOAD)
async def download_file(
    table: str,
    field: str,
    value: str,
    request: fa.Request,
    limit: int = 1,
    model: type[FastAdminMeta] = fa.Depends(FastAdminMeta._get_table),
    metainfo: MetaInfo = fa.Depends(FastAdminMeta.__get_metainfo__),
    access: types.AccessCredentials = fa.Depends(
        FastAdminConfig.admin_middleware.get_access_credentials
    ),
):
    session = model.get_session()

    async with session() as session:
        file, mediatype, filename = await model.download_file(
            session=session,
            table=table,
            field=field,
            value=value,
            limit=limit,
            metainfo=metainfo,
            access=access,
            request=request,
        )

        return fa.responses.StreamingResponse(
            file,
            media_type=mediatype,
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-Length": str(len(file.getvalue())),
            },
        )


@ui.get(urls.DOWNLOAD_PAGE, response_class=fa.responses.HTMLResponse)
async def download_page(table: str, field: str, value: str, limit: int = 1):
    page = """
    <div style="display:grid;place-content:center;height:100vh;">
        <p>Для заванатження файлу натисніть кнопку нижче:</p>
        <div style="text-align:center;">
            <button
              style="border:none;background-color: black;color: white;padding: 1rem;"
              id="downloadBtn"
            >Завантажити</button>
        </div>
    </div>
    <script>
        document.getElementById('downloadBtn').addEventListener('click', async () => {
            const requestUrl = `%(download_url)s`;

            try {
                const response = await fetch(requestUrl);
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                const blob = await response.blob();
                const downloadUrl = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.style.display = 'none';
                a.href = downloadUrl;

                const filename = response.headers.get('Content-Disposition').split('filename=')[1];
                a.download = filename;

                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(downloadUrl);
            } catch (error) {
                console.error('There was an error downloading the file:', error);
            }
        });
    </script>
    """

    download_url = (
        FastAdminConfig.api_root_url
        + urls.DOWNLOAD.format(table=table, field=field, value=value)
        + f"?limit={limit}"
    )

    return page % {"download_url": download_url}


@ui.get(
    urls.DOWNLOAD_REDIRECT,
    response_model=FastUI,
    response_model_exclude_none=True,
)
async def redirect_to_download_page(
    table: str, field: str, value: str, limit: int = 1
) -> list[c.AnyComponent]:
    url = (
        FastAdminConfig.api_root_url
        + urls.DOWNLOAD_PAGE.format(table=table, field=field, value=value)
        + f"?limit={limit}"
    )

    return [c.FireEvent(event=e.GoToEvent(url=url, target="_blank"))]


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
