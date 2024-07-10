from sqlalchemy.orm import Mapped, mapped_column

from fastadmin.utils.database.permissions import Permissions
from fastadmin.metadata import FastAdminMeta
from fastadmin.conf import FastAdminConfig

from fastui import events as e, components as c


def prem_validator(cls, v):
    if isinstance(v, list):
        return v
    return [v]


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
