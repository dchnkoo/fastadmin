from fastadmin.utils.database.asyn import _AsyncDB, _DB, Result
from fastadmin.conf import FastAdminConfig
import fastadmin.utils.types as _tb

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.sql import _typing as _sa_t
import sqlalchemy as _sa

import typing as _t


class ModelDB(_AsyncDB):
    @classmethod
    def get_session(
        cls: _t.Type[_DB],
        expire_on_commit: bool = False,
        info: _t.Optional[_sa_t._InfoType] = None,
        **kw,
    ) -> async_sessionmaker[AsyncSession]:
        global _ENGINE

        return async_sessionmaker(
            bind=_AsyncDB.create_engine(url=FastAdminConfig.sql_db_uri),
            class_=AsyncSession,
            expire_on_commit=expire_on_commit,
            info=info**kw,
        )

    @classmethod
    async def exists(cls: _t.Type[_DB], *args, session: AsyncSession) -> bool:
        return await super().exists(table=cls, *args, session=session)

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
        return await super().get(
            session=session,
            table=cls if table is None else table,
            where=where,
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
    async def insert(cls: _t.Type[_DB], session: AsyncSession, **kwargs) -> _DB:
        return await super().insert(table=cls, session=session, **kwargs)

    @classmethod
    async def update(
        cls: _t.Type[_DB],
        session: AsyncSession,
        where: _t.Optional[
            _t.Union[
                _sa_t.ColumnExpressionArgument, tuple[_sa_t.ColumnExpressionArgument]
            ]
        ] = None,
        **kwargs,
    ):
        await super().update(table=cls, session=session, where=where, **kwargs)

    @classmethod
    async def delete(
        cls: _t.Type[_DB],
        session: AsyncSession,
        where: _t.Union[
            _sa_t.ColumnExpressionArgument, tuple[_sa_t.ColumnExpressionArgument]
        ],
    ):
        await super().delete(
            table=cls,
            session=session,
            where=where,
        )
