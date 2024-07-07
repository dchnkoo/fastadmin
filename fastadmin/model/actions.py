from fastadmin.model.sqlmodel2pydantic import SQLModel2Pydantic
import typing as _t

if _t.TYPE_CHECKING:
    from fastadmin.metadata import FastAdminMeta, MetaInfo
    from fastadmin.middleware.jwt import AccessCredetinalsAdmin
    from sqlalchemy.ext.asyncio import AsyncSession
    from pydantic import BaseModel


class ModelActions(SQLModel2Pydantic):
    @classmethod
    def which_model(
        cls, model_type: _t.Literal["form", "edit_form", "admin", "repr"] = "repr"
    ) -> "BaseModel":
        return super().which_model(model=cls, model_type=model_type)

    @classmethod
    async def check_add_permissions(
        cls: type["FastAdminMeta"],
        user: "AccessCredetinalsAdmin",
        session: "AsyncSession",
        metainfo: "MetaInfo",
    ) -> bool:
        return user.is_super or (("add:" + cls.__name__) in user.permissions)

    @classmethod
    async def check_edit_permissions(
        cls: type["FastAdminMeta"],
        user: "AccessCredetinalsAdmin",
        session: "AsyncSession",
        metainfo: "MetaInfo",
    ) -> bool:
        return user.is_super or (("edit:" + cls.__name__) in user.permissions)

    @classmethod
    async def check_delete_permissions(
        cls: type["FastAdminMeta"],
        user: "AccessCredetinalsAdmin",
        session: "AsyncSession",
        metainfo: "MetaInfo",
    ) -> bool:
        return user.is_super or (("delete:" + cls.__name__) in user.permissions)
