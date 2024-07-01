from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
import sqlalchemy as sa

from fastadmin.metadata import FastAdminMeta
from fastadmin import FastAdmin


class Base(DeclarativeBase):
    ...


class Worker(FastAdminMeta, Base):
    __tablename__ = "some_worker"

    repr = {"exclude": ["id"]}

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String, nullable=False)


class User(Base, FastAdminMeta):
    __tablename__ = "some_user"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=True)
    worker: Mapped[int] = mapped_column(
        sa.ForeignKey("some_worker.id", link_to_name=True),
        nullable=False,
        doc="Работодавець",
        primary_key=True,
    )


app = FastAdmin(
    sql_db_uri="postgresql+asyncpg://test:test@localhost:5432/test",
    secret_token="sdihsbkfh",
    sqlalchemy_metadata=Base,
)
