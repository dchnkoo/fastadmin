import pydantic as _p
import typing as _t

import pytest

if _t.TYPE_CHECKING:
    from fastadmin import FastAdminTable


def test_sqlalchemy_table_info(table: "FastAdminTable"):
    table_info = table.__fastadmin_metadata__()

    assert len(table_info.primary_columns) == 1
    assert len(table_info.default_columns) == 4
    assert len(table_info.unique_columns) == 1
    assert len(table_info.index_columns) == 0
    assert len(table_info.nullable_columns) == 2
    assert len(table_info.foregin_colummns) == 0


def test_sqlalchemy_table_as_pydantic_model_serialization(table: "FastAdminTable"):
    table.as_pydantic_model()


def test_sqlalchemy_table_exclude_fields(table: "FastAdminTable"):
    model = table.as_pydantic_model(exclude=["id", "arr"])

    assert ("id" in model.model_fields) is False
    assert ("arr" in model.model_fields) is False
    assert ("name" in model.model_fields) is True
    assert ("additional" in model.model_fields) is True


def test_sqlalchemy_table_model_annotations(table: "FastAdminTable"):
    model = table.as_pydantic_model()

    assert model.model_fields["id"].annotation == int
    assert model.model_fields["name"].annotation == str
    assert model.model_fields["arr"].annotation == list[int]
    assert model.model_fields["additional"].annotation == dict


def test_sqlalchemy_table_frozen_field(table: "FastAdminTable"):
    model = table.as_pydantic_model()

    instance = model()

    with pytest.raises(_p.ValidationError) as exc_info:
        instance.id = 23

    assert exc_info.value.errors()[0]["msg"] == "Field is frozen"
