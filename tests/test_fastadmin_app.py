from fastadmin import FastAdminTable, FastColumn
from fastadmin import FastAdmin, AnyComponent
from fastadmin import Page

from fastapi.testclient import TestClient

import fastui.components as fc
import sqlalchemy as sa
import pytest


metadata = sa.MetaData()


class TestPage(Page, prefix="/test_prefix"):
    uri = "/test3"
    method = "GET"
    uri_type = "with_prefix"

    def render(self) -> str:
        return "TestPage"


class TestPageWithComponent(Page):
    uri = "/component"
    method = "GET"

    def render(self) -> list[AnyComponent]:
        return [fc.Page(components=[fc.Text(text="Hello World")])]


@pytest.fixture
def fastadmin_app():
    metadata = sa.MetaData()
    table = FastAdminTable(
        "test_table",
        metadata,
        FastColumn("id", sa.Integer, primary_key=True),
        FastColumn("name", sa.String, nullable=False),
    )
    app = FastAdmin(metadata=metadata, page_meta=Page)
    return app


def test_fastadmin_initialization(fastadmin_app: FastAdmin):
    assert fastadmin_app._title == "FastAdmin"
    assert fastadmin_app._root_url == "/admin"
    assert fastadmin_app._path_mode is None
    assert fastadmin_app._path_strip == "/prebuilt"


def test_fastadmin_routes(fastadmin_app: FastAdmin):
    client = TestClient(fastadmin_app)
    response = client.get("/admin/test_prefix/test3")
    assert response.headers["content-type"] == "text/html; charset=utf-8"
    assert response.status_code == 200
    assert response.text == "TestPage"


def test_fastadmin_component_route(fastadmin_app: FastAdmin):
    client = TestClient(fastadmin_app)
    response = client.get("/admin/component")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    assert response.json() == [
        {"components": [{"text": "Hello World", "type": "Text"}], "type": "Page"}
    ]


def test_fastadmin_invalid_metadata():
    with pytest.raises(ValueError) as exc_info:
        metadata = sa.MetaData()
        table = sa.Table(
            "invalid_table",
            metadata,
            sa.Column("id", sa.Integer, primary_key=True),
            sa.Column("name", sa.String, nullable=False),
        )
        FastAdmin(metadata=metadata, page_meta=Page)

    assert str(exc_info.value) == "metadata.tables must be FastAdminTable instances"


def test_fastadmin_routes(fastadmin_app: FastAdmin):
    pathes = [route.path for route in fastadmin_app.routes[4].app.routes]

    assert "/test_prefix/test3" in pathes
    assert "/component" in pathes
