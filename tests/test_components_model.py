from fastadmin.tools.components import BaseModelComponents
from fastadmin import FastAdminBase, FastColumn

from fastui import components as _c

import sqlalchemy as _sa


class BaseTestModel(BaseModelComponents):
    id: int
    name: str


class BaseFastTestModel(FastAdminBase):
    __tablename__ = "test_base_model"

    id = FastColumn(_sa.Integer, primary_key=True)
    name = FastColumn(_sa.String)


def test_as_model_form():
    form = BaseTestModel.as_model_form(submit_url="/submit")
    assert isinstance(form, _c.ModelForm)
    assert form.submit_url == "/submit"
    assert form.model == BaseTestModel


def test_as_form():
    instance = BaseTestModel(id=1, name="Test")
    form = instance.as_form(submit_url="/submit")
    assert isinstance(form, _c.ModelForm)
    assert form.submit_url == "/submit"
    assert form.initial == {"id": 1, "name": "Test"}
    assert form.model == BaseTestModel


def test_as_model_modal_form():
    modal = BaseTestModel.as_model_modal_form(title="Test Modal", submit_url="/submit")
    assert isinstance(modal, _c.Modal)
    assert modal.title == "Test Modal"
    assert isinstance(modal.body[0], _c.ModelForm)
    assert modal.body[0].submit_url == "/submit"
    assert modal.body[0].model == BaseTestModel


def test_as_modal_form():
    instance = BaseTestModel(id=1, name="Test")
    modal = instance.as_modal_form(title="Test Modal", submit_url="/submit")
    assert isinstance(modal, _c.Modal)
    assert modal.title == "Test Modal"
    assert isinstance(modal.body[0], _c.ModelForm)
    assert modal.body[0].initial == {"id": 1, "name": "Test"}
    assert modal.body[0].model == BaseTestModel


def test_as_details():
    instance = BaseTestModel(id=1, name="Test")
    details = instance.as_details()
    assert isinstance(details, _c.Details)
    assert details.data == instance


def test_as_model_table_with_dict():
    data = [{"id": 1, "name": "Test"}]

    model = BaseFastTestModel.as_pydantic_model()
    table = model.as_model_table(data)

    assert isinstance(table, _c.Table)
    assert len(table.data) == 1
    assert table.data[0].id == 1
    assert table.data[0].name == "Test"


def test_as_model_table_with_fastadmin_base():
    data = [BaseFastTestModel(id=1, name="Test")]

    model = BaseFastTestModel.as_pydantic_model()
    table = model.as_model_table(data)

    assert isinstance(table, _c.Table)
    assert len(table.data) == 1
    assert table.data[0].id == 1
    assert table.data[0].name == "Test"


def test_as_model_table_with_mixed_data():
    data = [{"id": 1, "name": "Test"}, BaseFastTestModel(id=1, name="Test")]

    model = BaseFastTestModel.as_pydantic_model()
    table = model.as_model_table(data)

    assert isinstance(table, _c.Table)
    assert len(table.data) == 2
    assert table.data[0].id == 1
    assert table.data[0].name == "Test"
    assert table.data[1].id == 1
    assert table.data[1].name == "Test"


def test_to_pydantic_model():
    instance = BaseFastTestModel(id=1, name="Test")
    model = instance.to_pydantic_model()

    assert isinstance(model, BaseModelComponents)
    assert model.id == 1
    assert model.name == "Test"


def test_fast_model_config():
    model = BaseFastTestModel.as_pydantic_model(
        exclude=["id"],
    )

    assert issubclass(model, BaseModelComponents)
    assert "id" not in model.model_fields
    assert "name" in model.model_fields

    assert model.fast_model_config == {
        "exclude": ["id"],
        "base": BaseModelComponents,
        "doc": None,
        "config": None,
        "module": "fastadmin.tools.tools",
        "validators": None,
        "cls_kwargs": None,
    }
