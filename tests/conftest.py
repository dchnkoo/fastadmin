from fastadmin import (
    FastAdminTable,
    FastColumn,
)

import sqlalchemy as _sa
import pytest


user_table = FastAdminTable(
    "users",
    _sa.MetaData(),
    FastColumn(
        "id",
        _sa.BigInteger,
        default_factory=lambda: 7136417639274,
        validate_default=True,
        frozen=True,
        primary_key=True,
    ),
    FastColumn(
        "name",
        _sa.String,
        default="Anonim",
        validate_default=True,
        unique=True,
    ),
    FastColumn(
        "additional",
        _sa.JSON,
        default_factory=dict,
        validate_default=True,
        nullable=False,
    ),
    FastColumn(
        "arr",
        _sa.ARRAY(_sa.Integer),
        default_factory=lambda: [1, 2, 3],
        min_length=3,
        validate_default=True,
        anotation=list[int],
    ),
)


@pytest.fixture(scope="session")
def table():
    return user_table
