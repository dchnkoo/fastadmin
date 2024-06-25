from sqlalchemy.orm import Mapped, mapped_column

from fastadmin.metadata import FastAdminMeta
from fastadmin.conf import FastAdminConfig


class AdminUser(FastAdminMeta, FastAdminConfig.sqlalchemy_metadata):
    __tablename__ = "admin_user"

    admin = {"exclude": []}

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(nullable=True)
    last_name: Mapped[str] = mapped_column(nullable=True)
    email: Mapped[str] = mapped_column(nullable=False, unique=True)
    is_admin: Mapped[bool] = mapped_column(nullable=False, default=False)
