import sqlalchemy as sa
import typing as _t

if _t.TYPE_CHECKING:
    from fastadmin.metadata import MetaInfo
    from sqlalchemy.ext.asyncio import AsyncSession


async def search_func(
    session: "AsyncSession",
    metainfo: "MetaInfo",
    field: _t.Optional[str],
    search: _t.Optional[str],
    **kw,
):
    where = []
    where_or = []

    table = metainfo.table

    if field is not None and search is not None:
        meta_field = metainfo.columns.get(field)

        where.append(getattr(table, meta_field.name) == meta_field.python_type(search))

    if field is None and search is not None:
        search = search.split(" ") if " " in search else [search]

        for key, _ in metainfo.columns.items():
            for word in search:
                where_or.append(
                    sa.cast(getattr(table, key), sa.String).ilike(f"%{word}%")
                )

    return await table.get(
        session=session, where=tuple(where), where_or=tuple(where_or), **kw
    )
