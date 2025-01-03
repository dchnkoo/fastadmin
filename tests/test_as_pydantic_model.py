from fastadmin.tools.tools import FastAdminTable, FastColumn, BaseModelComponents

import sqlalchemy as _sa
import pydantic as _p
import pytest


class CustomBaseModel(_p.BaseModel):
    custom_field: str = "custom"


class AnotherBaseModel(_p.BaseModel):
    another_field: str = "another"


@pytest.fixture
def table():
    return FastAdminTable(
        "test_table",
        _sa.MetaData(),
        FastColumn("id", _sa.Integer, primary_key=True),
        FastColumn("name", _sa.String, nullable=False),
    )


def test_as_pydantic_model_default_base(table: FastAdminTable):
    model = table.as_pydantic_model()
    assert issubclass(model, BaseModelComponents)


def test_as_pydantic_model_custom_base(table: FastAdminTable):
    model = table.as_pydantic_model(base=CustomBaseModel)
    assert issubclass(model, CustomBaseModel)
    assert issubclass(model, BaseModelComponents)


def test_as_pydantic_model_multiple_bases(table: FastAdminTable):
    model = table.as_pydantic_model(base=(CustomBaseModel, AnotherBaseModel))
    assert issubclass(model, CustomBaseModel)
    assert issubclass(model, AnotherBaseModel)
    assert issubclass(model, BaseModelComponents)


def test_as_pydantic_model_none_base(table: FastAdminTable):
    model = table.as_pydantic_model(base=None)
    assert issubclass(model, BaseModelComponents)
