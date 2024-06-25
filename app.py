from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
import sqlalchemy as sa

from fastadmin.metadata import FastAdminMeta
from fastadmin import FastAdmin

import pydantic as p


class Base(DeclarativeBase):
    ...


class Worker(FastAdminMeta, Base):
    __tablename__ = "some_worker"

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String, nullable=False)


from fastadmin.utils.database.tables import AdminUser  # noqa E402, F401


class User(Base, FastAdminMeta):
    __tablename__ = "some_user"

    __some__ = "ok"

    admin = {"exclude": ["id"], "fields": {"name": (bool, p.Field(title="Ім'я"))}}

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=True)
    worker: Mapped[int] = mapped_column(
        sa.ForeignKey("some_worker.id", link_to_name=True),
        nullable=False,
        doc="Работодавець",
        primary_key=True,
    )


app = FastAdmin(sql_db_uri="postgresql+asyncpg://test:test@localhost:5432/test")
