from fastadmin.utils.database.asyn import _AsyncDB, _DB, Result
import fastadmin.utils.types as _tb

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, AsyncEngine
from sqlalchemy.sql import _typing as _sa_t
import sqlalchemy as _sa

import typing as _t


class ModelDB(_AsyncDB):
    engine: AsyncEngine
    get_session: async_sessionmaker[AsyncSession]

    @classmethod
    async def exists(cls: _t.Type[_DB], *args, session: AsyncSession) -> bool:
        return await super(ModelDB, cls).exists(cls, *args, session=session)

    @classmethod
    async def get(
        cls: _t.Type[_DB],
        session: AsyncSession,
        table: _t.Optional[_tb.TableColumns] = None,
        where: _t.Optional[
            _t.Union[
                _sa_t.ColumnExpressionArgument, tuple[_sa_t.ColumnExpressionArgument]
            ]
        ] = None,
        where_or: _t.Optional[
            _t.Union[
                _sa_t.ColumnExpressionArgument, tuple[_sa_t.ColumnExpressionArgument]
            ]
        ] = None,
        having: _t.Optional[
            _t.Union[
                _sa_t.ColumnExpressionArgument, tuple[_sa_t.ColumnExpressionArgument]
            ]
        ] = None,
        count: bool = False,
        sum: _t.Optional[_t.Union[_t.Tuple[_sa.Column], _sa.Column]] = None,
        avg: _t.Optional[_t.Union[_t.Tuple[_sa.Column], _sa.Column]] = None,
        min: _t.Optional[_t.Union[_t.Tuple[_sa.Column], _sa.Column]] = None,
        max: _t.Optional[_t.Union[_t.Tuple[_sa.Column], _sa.Column]] = None,
        offset: _t.Optional[int] = None,
        limit: _t.Optional[int] = None,
        order_by: _t.Optional[_sa.Column] = None,
        group_by: _t.Optional[_sa.Column] = None,
        distinct: bool = False,
        all_: bool = True,
        to_dict: bool = False,
    ) -> Result:
        return await super(ModelDB, cls).get(
            session=session,
            table=cls if table is None else table,
            where=where,
            where_or=where_or,
            having=having,
            count=count,
            sum=sum,
            avg=avg,
            min=min,
            max=max,
            offset=offset,
            limit=limit,
            order_by=order_by,
            group_by=group_by,
            distinct=distinct,
            all_=all_,
            to_dict=to_dict,
        )

    @classmethod
    async def insert(
        cls: _t.Type[_DB], session: AsyncSession, commit: bool = True, **kwargs
    ) -> _DB:
        return await super(ModelDB, cls).insert(
            table=cls, session=session, commit=commit, **kwargs
        )

    @classmethod
    async def update(
        cls,
        session: AsyncSession,
        where: _t.Optional[
            _t.Union[
                _sa_t.ColumnExpressionArgument, tuple[_sa_t.ColumnExpressionArgument]
            ]
        ] = None,
        commit: bool = True,
        **kwargs,
    ):
        await super(ModelDB, cls).update(
            table=cls, session=session, where=where, commit=commit, **kwargs
        )

    @classmethod
    async def delete(
        cls,
        session: AsyncSession,
        where: _t.Union[
            _sa_t.ColumnExpressionArgument, tuple[_sa_t.ColumnExpressionArgument]
        ],
        commit: bool = True,
    ):
        await super(ModelDB, cls).delete(
            table=cls,
            session=session,
            where=where,
            commit=commit,
        )
