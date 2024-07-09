from sqlalchemy.orm import Mapped, mapped_column
import sqlalchemy as sa

from fastadmin.utils.descriptor.clas import classproperty
from fastadmin.metadata import FastAdminMeta
from fastadmin.conf import FastAdminConfig

from fastui import events as e, components as c

from enum import Enum
import pydantic as p
import typing as _t


def prem_validator(cls, v):
    if isinstance(v, list):
        return v
    return [v]


class Permissions:
    @classproperty
    def form(cls):
        perm_enum = Enum(
            "Permissions", {k.replace(":", "_"): k for k in cls._permissions}, type=str
        )

        return {
            "exclude": ["id"],
            "fields": {
                "permissions": (_t.Optional[list[perm_enum]], p.Field(default=[]))
            },
            "validators": {
                "premissions_validator": p.field_validator(
                    "permissions", check_fields=False, mode="before"
                )(prem_validator)
            },
        }

    @classproperty
    def edit_form(cls):
        get_form: dict = cls.form

        return {
            "exclude": get_form["exclude"] + ["password"],
            "fields": {"permissions": get_form["fields"]["permissions"]},
            "validators": get_form["validators"],
        }

    is_admin: Mapped[bool] = mapped_column(nullable=False, default=False)
    is_super: Mapped[bool] = mapped_column(nullable=False, default=False)
    permissions: Mapped[list[str]] = mapped_column(
        sa.ARRAY(sa.String),
        nullable=True,
        default=[],
    )


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

    repr = {"exclude": ["id", "password", "is_admin", "is_super", "permissions"]}
