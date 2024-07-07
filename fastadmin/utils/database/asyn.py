from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.sql import _typing as sa_t
import sqlalchemy as sa

from fastadmin.utils import types as _tb

import pydantic as p
import typing as _t


_DB = _t.TypeVar("_DB", bound="_AsyncDB")


class _AsyncDB:
    @staticmethod
    def create_engine(url: str, **kw):
        return create_async_engine(url=url, **kw)

    @classmethod
    def get_session(
        cls: _t.Type[_DB],
        engine: AsyncEngine,
        expire_on_commit: bool = False,
        info: _t.Optional[sa_t._InfoType] = None,
        **kw,
    ) -> async_sessionmaker[AsyncSession]:
        return async_sessionmaker(
            bind=engine,
            class_=AsyncSession,
            expire_on_commit=expire_on_commit,
            info=info**kw,
        )

    @staticmethod
    async def execute(
        session: AsyncSession, query: sa.Executable, commit: bool = False, **kwargs
    ) -> _t.Optional[sa.Result[_t.Any]]:
        async with session.begin():
            try:
                result = await session.execute(query, **kwargs)

            except Exception as e:
                await session.rollback()

                raise e

            else:
                if commit:
                    await session.commit()

                return result

    @classmethod
    async def use_sqlalchemy_function(
        cls: _t.Type[_DB],
        func: sa.Function,
        session: AsyncSession,
        where: _t.Optional[
            _t.Union[
                sa_t.ColumnExpressionArgument, tuple[sa_t.ColumnExpressionArgument]
            ]
        ] = None,
    ) -> _t.Any:
        query = sa.select(func).select_from(cls)

        if where is not None:
            query = query.where(
                sa.and_(*where) if isinstance(where, tuple) else sa.and_(where)
            )

        result = await cls.execute(session=session, query=query)

        return result.scalar()

    @classmethod
    async def use_sqlalchemy_functions(
        cls: _t.Type[_DB],
        funcs: tuple[sa.Function],
        session: AsyncSession,
        where: _t.Optional[
            _t.Union[
                sa_t.ColumnExpressionArgument, tuple[sa_t.ColumnExpressionArgument]
            ]
        ] = None,
    ) -> tuple[_t.Any]:
        return (
            await cls.use_sqlalchemy_function(func=func, session=session, where=where)
            for func in funcs
        )

    @classmethod
    async def exists(cls: _t.Type[_DB], table: sa.Table, *args, session: AsyncSession):
        result: Result = await cls.get(
            session=session, table=table, where=args, all_=False
        )

        return bool(result.data)

    @classmethod
    async def get(
        cls: _t.Type[_DB],
        session: AsyncSession,
        table: _t.Union[sa.Table, _tb.TableColumns],
        where: _t.Optional[
            _t.Union[
                sa_t.ColumnExpressionArgument, tuple[sa_t.ColumnExpressionArgument]
            ]
        ] = None,
        having: _t.Optional[
            _t.Union[
                sa_t.ColumnExpressionArgument, tuple[sa_t.ColumnExpressionArgument]
            ]
        ] = None,
        count: bool = False,
        sum: _t.Optional[_t.Union[_t.Tuple[sa.Column], sa.Column]] = None,
        avg: _t.Optional[_t.Union[_t.Tuple[sa.Column], sa.Column]] = None,
        min: _t.Optional[_t.Union[_t.Tuple[sa.Column], sa.Column]] = None,
        max: _t.Optional[_t.Union[_t.Tuple[sa.Column], sa.Column]] = None,
        offset: _t.Optional[int] = None,
        limit: _t.Optional[int] = None,
        order_by: _t.Optional[sa.Column] = None,
        group_by: _t.Optional[sa.Column] = None,
        distinct: bool = False,
        all_: bool = True,
        to_dict: bool = False,
    ) -> "Result":
        query: sa.Select = (
            sa.select(*table) if isinstance(table, tuple) else sa.select(table)
        )

        if distinct:
            query = query.distinct()

        if where is not None:
            query = query.where(
                sa.and_(*where) if isinstance(where, tuple) else sa.and_(where)
            )

        if count:
            count = await cls.use_sqlalchemy_function(
                sa.func.count(),
                session=session,
                where=where,
            )

        if sum is not None:
            sum = (
                await cls.use_sqlalchemy_functions(
                    tuple(sa.func.sum(column) for column in sum),
                    session=session,
                    where=where,
                )
                if isinstance(sum, tuple)
                else await cls.use_sqlalchemy_function(
                    sa.func.sum(sum), session=session, where=where
                )
            )

        if avg is not None:
            avg = (
                await cls.use_sqlalchemy_functions(
                    tuple(sa.func.avg(column) for column in avg),
                    session=session,
                    where=where,
                )
                if isinstance(avg, tuple)
                else await cls.use_sqlalchemy_function(
                    sa.func.avg(avg), session=session, where=where
                )
            )

        if min is not None:
            min = (
                await cls.use_sqlalchemy_functions(
                    tuple(sa.func.min(column) for column in min),
                    session=session,
                    where=where,
                )
                if isinstance(min, tuple)
                else await cls.use_sqlalchemy_function(
                    sa.func.min(min), session=session, where=where
                )
            )

        if max is not None:
            max = (
                await cls.use_sqlalchemy_functions(
                    tuple(sa.func.max(column) for column in max),
                    session=session,
                    where=where,
                )
                if isinstance(max, tuple)
                else await cls.use_sqlalchemy_function(
                    sa.func.max(max), session=session, where=where
                )
            )

        if offset is not None:
            query = query.offset(offset=offset)

        if limit is not None:
            query = query.limit(limit=limit)

        if order_by is not None:
            query = query.order_by(order_by)

        if group_by is not None and (max or min or sum or avg or count):
            query = query.group_by(group_by)

        if having is not None:
            query = (
                query.having(*having)
                if isinstance(having, tuple)
                else query.having(having)
            )

        result = await cls.execute(session=session, query=query)

        result = result.scalars().all() if all_ else result.scalars().first()

        if to_dict:
            result = (
                [cls.to_json(data) for data in result] if all_ else cls.to_json(result)
            )

        return Result(
            data=result,
            count=count if count else None,
            sum=sum,
            avg=avg,
            max=max,
            min=min,
        )

    @staticmethod
    async def insert(table: sa.Table, session: AsyncSession, **kwargs) -> sa.Table:
        data = table(**kwargs)

        async with session.begin():
            try:
                session.add(data)

            except Exception as e:
                await session.rollback()

                raise e

            await session.commit()

        return data

    @classmethod
    async def update(
        cls: _t.Type[_DB],
        table: sa.Table,
        session: AsyncSession,
        where: _t.Optional[
            _t.Union[
                sa_t.ColumnExpressionArgument, tuple[sa_t.ColumnExpressionArgument]
            ]
        ] = None,
        **kwargs,
    ):
        query = sa.update(table)

        if where is not None:
            query = query.where(
                sa.and_(*where) if isinstance(where, tuple) else sa.and_(where)
            )

        query = query.values(**kwargs)

        await cls.execute(session=session, query=query, commit=True)

    @classmethod
    async def delete(
        cls: _t.Type[_DB],
        table: sa.Table,
        session: AsyncSession,
        where: _t.Union[
            sa_t.ColumnExpressionArgument, tuple[sa_t.ColumnExpressionArgument]
        ],
    ):
        query = sa.delete(table).where(
            sa.and_(*where) if isinstance(where, tuple) else sa.and_(where)
        )

        await cls.execute(session=session, query=query, commit=True)

    @classmethod
    def to_json(cls, data: _t.Type[_DB]) -> dict:
        return data._asdict() if hasattr(data, "_asdict") else cls._dump_json(data)

    @staticmethod
    def _dump_json(table: _t.Type[_DB]) -> dict:
        return {
            column.name: getattr(table, column.name)
            for column in table.__table__.columns
        }


class Result(p.BaseModel):
    data: _t.Optional[_t.Union[_t.Any, tuple[_t.Any]]]
    count: _t.Optional[_t.Union[int, tuple[int]]] = 0
    sum: _t.Optional[_t.Union[float, tuple[float]]] = 0
    avg: _t.Optional[_t.Union[float, tuple[float]]] = 0
    min: _t.Optional[_t.Union[_t.Any, tuple[_t.Any]]] = None
    max: _t.Optional[_t.Union[_t.Any, tuple[_t.Any]]] = None
