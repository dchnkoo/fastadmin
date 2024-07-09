from typing import Any, Literal
from pydantic import BaseModel
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from fastadmin.middleware.jwt import AccessCredetinalsAdmin
from fastadmin.utils.database.enum import set_enum
from fastadmin.metadata import FastAdminMeta, MetaInfo
from fastadmin.utils.words import AdminWords
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

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String, nullable=False)

    form = {"exclude": ["id"]}

    edit_form = {"exclude": form["exclude"]}


class User(Base, FastAdminMeta):
    __tablename__ = "some_user"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=True)

    status = mapped_column(set_enum(Status, "user_status"), nullable=False)

    worker: Mapped[int] = mapped_column(
        sa.ForeignKey("some_worker.id", link_to_name=True),
        nullable=False,
        doc={"foregin": {"selected_foregin_field": "name"}},
    )

    form = {"exclude": ["id"]}

    edit_form = {"exclude": form["exclude"]}

    @classmethod
    async def before_saving(
        cls: FastAdminMeta,
        signal: Literal["form"] | Literal["edit_form"],
        session: AsyncSession,
        data: dict[str, Any],
        model: type[BaseModel],
        access: AccessCredetinalsAdmin,
        table_name: str,
        metainfo: MetaInfo,
        **kw,
    ) -> None:
        data["worker"] = int(data["worker"])


words = AdminWords(
    add="Додати",
    logout="Вийти",
    logout_question="Ви впевнені що хочете вийти з акаунту?",
    cancel="Скасувати",
    additional_information="Додаткова інформація:",
    delete="Видалити",
    confirm_operation="Підтвердіть дію",
    operation_delete_question="Ви впевнені що хочете видалити елемент з {field} - {value} з таблиці {table}?",
    back="Назад",
    edit="Редагувати",
    form_page_heading="Додати до %s",
    edit_page_heading="Редагувати %s",
)

app = FastAdmin(
    sql_db_uri="postgresql+asyncpg://test:test@localhost:5432/test",
    secret_token="sdihsbkfh",
    sqlalchemy_metadata=Base,
    admin_panel_words=words,
    default_title="Електрична Фортеця Admin",
)
