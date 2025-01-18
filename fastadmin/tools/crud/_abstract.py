import sqlalchemy as _sa

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tools.tools import FastAdminBase


class AbstractCRUD[_TB: type["FastAdminBase"]]:
    @classmethod
    def query_get_by_primary_key[_T](cls: _TB, value: _T):
        prymary_key = cls.primary_key()

        return _sa.select(cls).where(prymary_key == value)
