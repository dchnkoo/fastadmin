import sqlalchemy as sa
import typing as _t


Table: _t.TypeAlias = object
TableColumns: _t.TypeAlias = tuple[sa.Column]

TableStrName: _t.TypeAlias = str

URI_WITH_ASYNC_DRIVER: _t.TypeAlias = str

FastModels: _t.TypeAlias = _t.Literal["form", "edit_form", "admin", "repr"]

AccessCredentials: _t.TypeAlias = _t.Any
