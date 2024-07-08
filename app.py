from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
import sqlalchemy as sa

from fastadmin.utils.database.enum import set_enum
from fastadmin.metadata import FastAdminMeta
from fastadmin import FastAdmin

from enum import Enum


class Base(DeclarativeBase):
    ...


class Status(Enum):
    blocked = "Заблокованний"
    inactive = "Неактивний"
    active = "Активний"


class Worker(FastAdminMeta, Base):
    __tablename__ = "some_worker"

    repr = {"exclude": ["id"]}

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String, nullable=False)


class User(Base, FastAdminMeta):
    __tablename__ = "some_user"

    __title__ = "Користувач"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=True)

    status = mapped_column(set_enum(Status, "user_status"), nullable=False)

    worker: Mapped[int] = mapped_column(
        sa.ForeignKey("some_worker.id", link_to_name=True),
        nullable=False,
        doc={"title": "Работодавець", "foregin": {"selected_foregin_field": "name"}},
        primary_key=True,
    )


app = FastAdmin(
    sql_db_uri="postgresql+asyncpg://test:test@localhost:5432/test",
    secret_token="sdihsbkfh",
    sqlalchemy_metadata=Base,
)
