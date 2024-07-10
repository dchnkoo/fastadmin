import sqlalchemy as sa
import typing as _t

from fastapi import params as _params
import fastapi as _fa
import fastui.forms as _forms
import pydantic as _p

if _t.TYPE_CHECKING:
    from fastadmin.metadata import MetaInfo
    from sqlalchemy.ext.asyncio import AsyncSession


async def search_func(
    session: "AsyncSession",
    metainfo: "MetaInfo",
    field: _t.Optional[str],
    search: _t.Optional[str],
    enums: dict[str, str] = {},
    bools: dict[str, str] = {},
    ilike: bool = False,
    **kw,
):
    where = []
    where_or = []

    table = metainfo.table

    if field is not None and search is not None:
        meta_field = metainfo.columns.get(field)

        if ilike:
            where.append(
                sa.cast(getattr(table, meta_field.name), sa.String).ilike(f"%{search}%")
            )
        else:
            where.append(
                getattr(table, meta_field.name) == meta_field.python_type(search)
            )

    if field is None and search is not None:
        search = search.split(" ") if " " in search else [search]

        for key, _ in metainfo.columns.items():
            for word in search:
                where_or.append(
                    sa.cast(getattr(table, key), sa.String).ilike(f"%{word}%")
                )

    for name, value in enums.items():
        meta_enum_column = metainfo.enum_columns.get(name)

        where.append(
            getattr(table, meta_enum_column.name) == meta_enum_column.python_type(value)
        )

    for name, value in bools.items():
        meta_bool_column = metainfo.bool_columns.get(name)

        where.append(
            getattr(table, meta_bool_column.name).is_(
                meta_bool_column.python_type(value)
            )
        )

    return await table.get(
        session=session, where=tuple(where), where_or=tuple(where_or), **kw
    )


def patched_fastui_form(model: type[_forms.FormModel]) -> _params.Depends:
    """
    FastUI have bug when you try upload files from form and file
    come to server already closed. For fix this use this pathced function.
    """

    async def run_fastui_form(request: _fa.Request):
        async with request.form() as form_data:
            model_data = _forms.unflatten(form_data)

            try:
                yield model.model_validate(model_data)
            except _p.ValidationError as e:
                raise _fa.HTTPException(
                    status_code=422,
                    detail={
                        "form": e.errors(
                            include_input=False,
                            include_url=False,
                            include_context=False,
                        )
                    },
                )

    return _fa.Depends(run_fastui_form)
