from fastadmin.tools.components import BaseModelComponents
from fastui import components as _c


class BaseTestModel(BaseModelComponents):
    id: int
    name: str


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
