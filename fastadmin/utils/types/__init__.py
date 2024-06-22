import sqlalchemy as sa
import typing as _t


Table: _t.TypeAlias = object
TableColumns: _t.TypeAlias = tuple[sa.Column]

TableStrName: _t.TypeAlias = str
