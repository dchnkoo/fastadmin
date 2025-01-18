from fastadmin import Page as _page, PageMeta

from fastapi import responses

import pytest


class Page(_page):
    __pagemeta__ = PageMeta()

    def render(self) -> responses.HTMLResponse: ...


class TestPageOnlyPage(Page):
    uri = "/test"

    def render(self) -> responses.HTMLResponse:
        return "TestPageOnlyPage"


class TestPageWithPrefix(Page, prefix="/prefix"):
    uri = "/test2"

    def render(self) -> responses.HTMLResponse:
        return "TestPageWithPrefix"


class TestPageWithParent(TestPageOnlyPage):
    uri = "/child"

    def render(self) -> responses.HTMLResponse:
        return "TestPageWithParent"


class TestPageWithMultipleInheritance(Page):
    uri = "/multiple"

    def render(self) -> responses.HTMLResponse:
        return "TestPageWithMultipleInheritance"


def test_page_uri():
    assert TestPageOnlyPage.get_uri() == "/test"
    assert TestPageWithPrefix.get_uri() == "/prefix/test2"
    assert TestPageWithParent.get_uri() == "/test/child"
    assert TestPageWithParent.get_uri() == "/test/child"


def test_page_inheritance():
    assert TestPageWithParent._parent == TestPageOnlyPage
    assert TestPageWithParent.get_versions() == [TestPageOnlyPage]


def test_page_multiple_inheritance():
    with pytest.raises(ValueError) as exc_info:

        class InvalidPage(TestPageOnlyPage, TestPageWithPrefix):
            uri = "/invalid"

    assert "Multiple inheritance" in str(exc_info.value)
    assert "is not allowed" in str(exc_info.value)


def test_page_duplicate_uri():
    with pytest.raises(ValueError) as exc_info:

        class DuplicatePage(Page):
            uri = "/test"

    assert "URI `/test` is already used by `TestPageOnlyPage`" in str(exc_info.value)


def test_page_prefix_validation():
    with pytest.raises(ValueError) as exc_info:

        class InvalidPrefixPage(Page, prefix="invalid"):
            uri = "/invalid"

    assert "Prefix must start with a `/`" in str(exc_info.value)


def test_page_uri_validation():
    with pytest.raises(ValueError) as exc_info:

        class InvalidUriPage(Page):
            uri = "invalid"

    assert "URI must start with a `/`" in str(exc_info.value)


def test_page_render():
    page = TestPageOnlyPage()
    assert page.render() == "TestPageOnlyPage"


def test_page_str():
    page = TestPageOnlyPage()
    assert str(page) == "<TestPageOnlyPage /test>"


def test_page_repr():
    page = TestPageOnlyPage()
    assert repr(page) == "<TestPageOnlyPage /test>"


def test_page_hash():
    page = TestPageOnlyPage()
    assert hash(page) == hash("/test")


def test_render_merhod_ovveride_like_variable():
    with pytest.raises(ValueError) as exc_info:

        class TestPageOverride(Page):
            uri = "/TestPageOverride"

            render = "TestPageOverride"

    assert "Page must have a `render` method" in str(exc_info.value)


def test_page_missing_render_method():
    with pytest.raises(ValueError) as exc_info:

        class MissingRenderMethodPage(Page):
            uri = "/missing"

    assert "Page `render` method must be a method of the class" in str(exc_info.value)


def test_page_invalid_render_method():
    with pytest.raises(ValueError) as exc_info:

        class InvalidRenderMethodPage(Page):
            uri = "/InvalidRenderMethodPage"

            def render(self):
                pass

    assert "Page `render` method must have a return annotation" in str(exc_info.value)


def test_page_invalid_render_return_type():
    with pytest.raises(ValueError) as exc_info:

        class InvalidRenderReturnTypePage(Page):
            uri = "/invalid_return_type"

            def render(self) -> int:
                return 123

    assert f"Page `render` method must return one of" in str(exc_info.value)


def test_page_invalid_api_method():
    with pytest.raises(ValueError) as exc_info:

        class InvalidApiMethod(Page):
            uri = "/InvalidApiMethod"

            method = "INVALID"

            def render(self) -> responses.HTMLResponse:
                return ...

    assert "Method must be one of" in str(exc_info.value)
