from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from fastadmin.middleware.jwt import AccessCredetinalsAdmin
from fastadmin.utils.database.permissions import Permissions
from fastadmin.metadata import FastAdminMeta, MetaInfo
from fastadmin.utils.func import hash_password
from fastadmin.conf import FastAdminConfig

from fastui import events as e, components as c
import typing as _t


class AdminUser(Permissions, FastAdminMeta, FastAdminConfig.sqlalchemy_metadata):
    __tablename__ = FastAdminConfig.admin_table_name

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(nullable=True)
    last_name: Mapped[str] = mapped_column(nullable=True)
    email: Mapped[str] = mapped_column(nullable=False, unique=True)
    password: Mapped[str] = mapped_column(nullable=False)

    display_lookups = [
        c.display.DisplayLookup(
            field="email", on_click=e.GoToEvent(url="./email/{email}")
        ),
        c.display.DisplayLookup(field="first_name"),
        c.display.DisplayLookup(field="last_name"),
        c.display.DisplayLookup(field="is_super"),
    ]

    admin = {"exclude": ["id", "password"]}

    repr = {"exclude": admin["exclude"] + ["is_admin", "is_super", "permissions"]}

    @classmethod
    async def before_saving(
        cls,
        signal: _t.Literal["form", "edit_form"],
        session: AsyncSession,
        data: dict[str, _t.Any],
        model: type[BaseModel],
        access: AccessCredetinalsAdmin,
        table_name: str,
        metainfo: MetaInfo,
        **kw,
    ) -> None:
        if signal == "form":
            data["password"] = hash_password(data["password"])
