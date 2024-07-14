from fastadmin.model.sqlmodel2pydantic import SQLModel2Pydantic
from fastadmin.conf import FastAdminConfig
from fastadmin.utils import types

import fastapi as _fa
import sqlalchemy as sa
import pydantic as p
import typing as _t

if _t.TYPE_CHECKING:
    from fastadmin.metadata import FastAdminMeta, MetaInfo
    from fastadmin.middleware.jwt import AccessCredetinalsAdmin
    from sqlalchemy.ext.asyncio import AsyncSession
    from pydantic import BaseModel
    from io import BytesIO


T = _t.TypeVar("T")

mediatype: _t.TypeAlias = str
filename: _t.TypeAlias = str


class ModelActions(SQLModel2Pydantic):
    @classmethod
    def which_model(
        cls, model_type: _t.Literal["form", "edit_form", "admin", "repr"] = "repr"
    ) -> "BaseModel":
        return super().which_model(model=cls, model_type=model_type)

    @classmethod
    def call_check_permissions_funcion(cls: type["FastAdminMeta"], func_name: str):
        async def check_permissions(
            table: str,
            access: types.AccessCredentials = _fa.Depends(
                FastAdminConfig.admin_middleware.get_access_credentials
            ),
        ):
            metainfo = cls.__get_metainfo__(table=table)
            model = metainfo.table

            session = model.get_session()

            func: _t.Callable = getattr(model, func_name)

            async with session() as session:
                if (
                    await func(user=access, session=session, metainfo=metainfo)
                ) is False:
                    raise _fa.HTTPException(status_code=_fa.status.HTTP_423_LOCKED)

        return check_permissions

    @classmethod
    async def check_add_permissions(
        cls: type["FastAdminMeta"],
        user: "AccessCredetinalsAdmin",
        session: "AsyncSession",
        metainfo: "MetaInfo",
    ) -> bool:
        return (
            user.is_super or ("add:" + cls.__name__ in user.permissions)
        ) and cls.can_add

    @classmethod
    async def check_edit_permissions(
        cls: type["FastAdminMeta"],
        user: "AccessCredetinalsAdmin",
        session: "AsyncSession",
        metainfo: "MetaInfo",
    ) -> bool:
        return (
            user.is_super or ("edit:" + cls.__name__ in user.permissions)
        ) and cls.can_edit

    @classmethod
    async def check_delete_permissions(
        cls: type["FastAdminMeta"],
        user: "AccessCredetinalsAdmin",
        session: "AsyncSession",
        metainfo: "MetaInfo",
    ) -> bool:
        return (
            user.is_super or ("delete:" + cls.__name__ in user.permissions)
        ) and cls.can_delete

    @staticmethod
    def convert_integerstr_to_int(data: dict[str, T], ignore_fields: list[str]) -> None:
        for key, value in data.items():
            if (
                ("id" in key) or (isinstance(value, str) and value.isdigit())
            ) and key not in ignore_fields:
                data[key] = int(value)

    @classmethod
    async def before_saving(
        cls: type["FastAdminMeta"],
        signal: _t.Literal["form", "edit_form"],
        session: "AsyncSession",
        data: dict[str, _t.Any],
        model: type[p.BaseModel],
        access: "AccessCredetinalsAdmin",
        table_name: str,
        metainfo: "MetaInfo",
        **kw,
    ) -> None:
        if signal == "edit_form":
            await cls.combine_files(
                session=session,
                data=data,
                field=kw.get("field"),
                value=kw.get("value"),
                metainfo=metainfo,
            )

        else:
            await cls.convert_file_obj_to_bytes(data)

    @classmethod
    async def after_saving(
        cls: type["FastAdminMeta"],
        signal: _t.Literal["form", "edit_form"],
        session: "AsyncSession",
        data: type[sa.Table],
        model: type[p.BaseModel],
        access: "AccessCredetinalsAdmin",
        table_name: str,
        metainfo: "MetaInfo",
        **kw,
    ) -> None:
        ...

    @classmethod
    async def before_edit_view_page(
        cls: type["FastAdminMeta"],
        session: "AsyncSession",
        table: str,
        field: str,
        value: str,
        metainfo: "MetaInfo",
        access: types.AccessCredentials,
        data: dict,
    ) -> dict:
        return data

    @classmethod
    async def before_delete(
        cls: type["FastAdminMeta"],
        table: str,
        field: str,
        value: str,
        metainfo: "MetaInfo",
        access: types.AccessCredentials,
        data: dict,
    ):
        ...

    @classmethod
    async def after_delete(
        cls: type["FastAdminMeta"],
        table: str,
        field: str,
        value: str,
        metainfo: "MetaInfo",
        access: types.AccessCredentials,
        data: dict,
    ):
        ...

    @staticmethod
    def get_params_values_with_prefix(prefix: str):
        def get(request: _fa.Request) -> dict[str, str]:
            params = {}

            for key, value in request.query_params.items():
                if key.startswith(prefix):
                    params[key.removeprefix(prefix)] = value

            return params

        return get

    @classmethod
    async def download_file(
        cls: type["FastAdminMeta"],
        session: "AsyncSession",
        table: str,
        field: str,
        value: str,
        limit: int,
        metainfo: "MetaInfo",
        access: "AccessCredetinalsAdmin",
    ) -> tuple["BytesIO", mediatype, filename]:
        raise NotImplementedError

    @classmethod
    async def convert_to_selected_search_fields_foregins(
        cls: type["FastAdminMeta"],
        session: "AsyncSession",
        metainfo: "MetaInfo",
        data: dict,
    ) -> None:
        for column in metainfo.foregin_columns.values():
            foregin_table = cls._get_table(column.foregin_key.table_name)
            foregin_column = column.foregin_key.field_name

            foregin_data = (
                await foregin_table.get(
                    session=session,
                    where=getattr(foregin_table, foregin_column) == data[column.name],
                    all_=False,
                )
            ).data

            data[column.name] = {
                "value": str(getattr(foregin_data, foregin_column)),
                "label": str(
                    getattr(foregin_data, column.options.foregin.selected_foregin_field)
                ),
            }
