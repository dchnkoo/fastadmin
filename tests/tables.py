from fastadmin import (
    fastadmin_mapped_column,
    FastAdminTable,
    FastColumn,
    FastBase,
)
from sqlalchemy.orm import mapped_column, Mapped
import sqlalchemy as _sa


class User(FastBase):
    __tablename__ = "users"

    id: Mapped[int] = fastadmin_mapped_column(
        _sa.Integer, primary_key=True, frozen=True
    )
    name: Mapped[str] = mapped_column(_sa.String, nullable=False)
    age: Mapped[int] = fastadmin_mapped_column(_sa.Integer, nullable=True)


class Post(FastBase):
    __tablename__ = "posts"
    id = FastColumn(_sa.Integer, primary_key=True)
    title = _sa.Column(_sa.String, nullable=False)
    content = FastColumn(_sa.String, nullable=False, anotation=str)
    user_id = _sa.Column(_sa.Integer, _sa.ForeignKey("users.id"))


Comment = FastAdminTable(
    "comments",
    FastBase.metadata,
    FastColumn("id", _sa.Integer, primary_key=True),
    FastColumn("content", _sa.String, nullable=False),
    FastColumn("post_id", _sa.Integer, _sa.ForeignKey("posts.id")),
    _sa.Column("user_id", _sa.Integer, _sa.ForeignKey("users.id")),
)
