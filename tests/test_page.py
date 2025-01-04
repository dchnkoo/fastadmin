from fastadmin import Page

import pytest


class TestPage(Page):
    uri = "/test"


class TestPageWithPrefix(Page, prefix="/prefix"):
    uri = "/test2"


class TestPageWithParent(TestPage):
    uri = "/child"


class TestPageWithMultipleInheritance(Page):
    uri = "/multiple"


def test_page_uri():
    assert TestPage.page_uri() == "/test"
    assert TestPageWithPrefix.page_uri() == "/prefix/test2"
    assert TestPageWithParent.page_uri() == "/child"
    assert TestPageWithParent.page_uri(include_parents=True) == "/test/child"


def test_page_inheritance():
    assert TestPageWithParent._parent == TestPage
    assert TestPageWithParent._get_parents() == [TestPage]


def test_page_multiple_inheritance():
    with pytest.raises(ValueError):

        class InvalidPage(TestPage, TestPageWithPrefix):
            uri = "/invalid"


def test_page_duplicate_uri():
    with pytest.raises(ValueError):

        class DuplicatePage(Page):
            uri = "/test"


def test_page_prefix_validation():
    with pytest.raises(ValueError):

        class InvalidPrefixPage(Page, prefix="invalid"):
            uri = "/invalid"


def test_page_uri_validation():
    with pytest.raises(ValueError):

        class InvalidUriPage(Page):
            uri = "invalid"


def test_page_render():
    page = TestPage()
    assert page.render() is None


def test_page_str():
    page = TestPage()
    assert str(page) == "<TestPage /test>"


def test_page_repr():
    page = TestPage()
    assert repr(page) == "<TestPage /test>"


def test_page_hash():
    page = TestPage()
    assert hash(page) == hash("/test")
