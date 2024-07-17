from typing import Any, Literal
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from fastadmin.middleware.jwt import AccessCredetinalsAdmin
from fastadmin.utils.database.enum import set_enum
from fastadmin.utils.database.permissions import prem_validator
from fastadmin.metadata import FastAdminMeta, MetaInfo
from fastadmin.utils.words import AdminWords
from fastadmin import FastAdmin

from enum import Enum, StrEnum

from starlette import datastructures as dastrc  # noqa F401

from fastui import forms  # noqa F401
import typing as _t  # noqa F401
import fastapi as _fa  # noqa F401

import pydantic as p


class Base(DeclarativeBase):
    ...


class Status(Enum):
    blocked = "Заблокованний"
    inactive = "Неактивний"
    active = "Активний"


def images_validator(cls, v):
    if v is None:
        return []

    return prem_validator(cls, v)


LIMITS = Enum("Limits", {f"num_{v}": str(v) for v in range(10, 101, 10)}, type=str)


class Worker(FastAdminMeta, Base):
    __tablename__ = "some_worker"

    id = sa.Column(sa.Integer, primary_key=True)

    image = sa.Column(sa.LargeBinary, nullable=True)
    images = sa.Column(sa.ARRAY(sa.LargeBinary), nullable=True)

    name = sa.Column(sa.String, nullable=False)

    download = {
        "table": "some_user",
        "field": "worker",
        "limit": LIMITS,
        "value": lambda data: data.get("id"),
    }

    form = {
        "exclude": ["id"],
        "fields": {
            "image": (
                _t.Optional[_t.Annotated[_fa.UploadFile, forms.FormFile("image/*")]],
                p.Field(default=None),
            ),
            "images": (
                _t.Annotated[list[_fa.UploadFile], forms.FormFile("image/*")],
                p.Field(default=[]),
            ),
        },
    }

    edit_form = {
        "exclude": form["exclude"],
        "fields": form["fields"],
    }

    repr = {"exclude": edit_form["exclude"]}

    admin = {"exclude": ["image", "images"]}

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
    ) -> dict:
        del data["images"]
        del data["image"]

        return data


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
        model: type[p.BaseModel],
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

        return data


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
    secret_token="sdihsbkfh",
    sqlalchemy_metadata=Base,
    admin_panel_words=words,
    default_title="Електрична Фортеця Admin",
    files_height=300,
)
