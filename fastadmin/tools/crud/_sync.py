from ._abstract import AbstractCRUD

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tools.tools import FastAdminBase


class SyncCRUD[_TB: (type["FastAdminBase"], type[AbstractCRUD])](AbstractCRUD):
    @classmethod
    def get[_T](cls: _TB, value: _T):
        query = cls.query_get_by_primary_key(value)  # noqa F841
