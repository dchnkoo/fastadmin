from fastadmin import FastAdminTable, FastColumn
from fastadmin import FastUIRouter, AnyComponent
from fastadmin import Page as _page, PageMeta

from fastadmin.config import ROOT_URL, PATH_STRIP

from fastapi.testclient import TestClient
from fastapi import Request, responses

import fastui.components as fc
import sqlalchemy as sa
import pytest


metadata = sa.MetaData()


class AppPage(_page):
    __pagemeta__ = PageMeta()


class AppPage2(_page):
    __pagemeta__ = PageMeta()


class TestPage(AppPage, prefix="/test_prefix"):
    uri = "/test3"

    def render(self) -> responses.HTMLResponse:
        return "TestPage"


class TestPageWithComponent(AppPage):
    uri = "/component"

    def render(self, request: Request) -> list[AnyComponent]:
        assert isinstance(request, Request)
        return [fc.Page(components=[fc.Text(text="Hello World")])]


class TestPageWithParentsUri(TestPageWithComponent):
    uri = "/home"

    def render(self) -> responses.HTMLResponse:
        return "Hello World"


class TestPageForMount(AppPage2):
    uri = "/mount"

    def render(self) -> responses.HTMLResponse:
        return "Mount"


class TestPageForMount2(AppPage2):
    uri = "/mount2"

    def render(self) -> responses.HTMLResponse:
        return "Mount2"


@pytest.fixture(scope="session")
def fastadmin_app():
    metadata = sa.MetaData()
    table = FastAdminTable(
        "test_table",
        metadata,
        FastColumn("id", sa.Integer, primary_key=True),
        FastColumn("name", sa.String, nullable=False),
    )
    app = FastUIRouter(
        metadata=metadata, page_meta=AppPage.__pagemeta__, title="FastUI"
    )
    return app


def test_fastadmin_initialization(fastadmin_app: FastUIRouter):
    assert fastadmin_app.title == "FastUI"
    assert fastadmin_app.page_meta.root_url == ROOT_URL
    assert fastadmin_app._path_mode is None
    assert fastadmin_app.page_meta.path_strip == PATH_STRIP


def test_fastadmin_routes(fastadmin_app: FastUIRouter):
    client = TestClient(fastadmin_app)
    response = client.get(TestPage.get_uri())
    assert response.headers["content-type"] == "text/html; charset=utf-8"
    assert response.status_code == 200
    assert response.text == "TestPage"


def test_fastadmin_component_route(fastadmin_app: FastUIRouter):
    client = TestClient(fastadmin_app)
    response = client.get(TestPageWithComponent.get_uri())
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
        FastUIRouter(metadata=metadata, page_meta=AppPage)

    assert str(exc_info.value) == "metadata.tables must be FastAdminTable instances"


def test_fastadmin_app_routes(fastadmin_app: FastUIRouter):
    pathes = [route.path for route in fastadmin_app.routes[4].app.routes]

    assert "/test_prefix/test3" in pathes
    assert "/component" in pathes


def test_fastadmin_prebuilt_route(fastadmin_app: FastUIRouter):
    client = TestClient(fastadmin_app)
    response = client.get(PATH_STRIP)

    assert response.status_code == 200
    assert response.headers["content-type"] == "text/html; charset=utf-8"
    assert response.text.startswith("<!doctype html>")


def test_fastadmin_page_with_parents_uri(fastadmin_app: FastUIRouter):
    assert TestPageWithParentsUri.get_uri() == ROOT_URL + "/component/home"

    client = TestClient(fastadmin_app)
    response = client.get(TestPageWithParentsUri.get_uri())

    assert response.status_code == 200
    assert response.text == "Hello World"


def test_fastadmin_page_with_router_prefix(fastadmin_app: FastUIRouter):
    assert TestPageWithParentsUri.get_uri() == ROOT_URL + "/component/home"


def test_fastadmin_mount():
    app = FastUIRouter(
        metadata=metadata, page_meta=AppPage.__pagemeta__, title="FastUI"
    )
    sub_app = FastUIRouter(
        metadata=metadata, page_meta=AppPage2.__pagemeta__, title="SubApp"
    )
    app.mount("/sub", sub_app)
    assert sub_app.page_meta.mount_path == "/sub"
    assert TestPageForMount2.get_uri() == "/sub" + ROOT_URL + "/mount2"

    client = TestClient(app)

    response = client.get(TestPageForMount2.get_uri())

    assert response.status_code == 200
    assert response.text == "Mount2"
