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

from enum import Enum, StrEnum

from fastui import forms  # noqa F401
import typing as _t  # noqa F401
import fastapi as _fa  # noqa F401
import pydantic as p  # noqa F401


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

    can_delete = False

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=True)

    status = mapped_column(set_enum(Status, "user_status"), nullable=False)

    worker: Mapped[int] = mapped_column(
        sa.ForeignKey("some_worker.id", link_to_name=True),
        nullable=False,
        doc={"foregin": {"selected_foregin_field": "name"}},
    )

    form = {
        "exclude": ["id"],
    }

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

    @classmethod
    async def before_edit_view_page(
        cls: FastAdminMeta,
        session: AsyncSession,
        table: str,
        field: str,
        value: str,
        metainfo: MetaInfo,
        access: Any,
        data: dict,
    ) -> None:
        worker = await Worker.get(
            session=session,
            where=Worker.id == data.get("worker"),
            all_=False,
        )

        data["worker"] = {"value": worker.data.id, "label": worker.data.name}


class OrderStatus(StrEnum):
    new = "Новий"
    in_precessing = "В обробці"
    sent = "Відправлено"
    delivered = "Доставлено"
    canceled = "Відмінено"


class Order(Base, FastAdminMeta):
    __tablename__ = "order"

    hide_in_link = True

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    status: Mapped[OrderStatus] = mapped_column(
        set_enum(OrderStatus, "order_status"),
        default=OrderStatus.new.value,
        nullable=False,
    )
    registered_user: Mapped[bool] = mapped_column(default=False, nullable=False)


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
    search="Пошук",
    filter_text="Фільтри",
)

app = FastAdmin(
    sql_db_uri="postgresql+asyncpg://test:test@localhost:5432/test",
    secret_token="sdihsbkfh",
    sqlalchemy_metadata=Base,
    admin_panel_words=words,
    default_title="Електрична Фортеця Admin",
)
