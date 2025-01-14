import pytest

from fastadmin.tools.tracker import InheritanceTracker


class BaseClass(InheritanceTracker):
    pass


class DerivedClass(BaseClass):
    pass


class AnotherDerivedClass(DerivedClass):
    pass


class AnotherBaseClass(InheritanceTracker):
    pass


def test_single_inheritance():
    assert DerivedClass._parent == None
    assert DerivedClass.get_versions() == []


def test_multiple_inheritance_error():
    with pytest.raises(ValueError) as exc_info:

        @InheritanceTracker
        class InvalidClass(DerivedClass, AnotherBaseClass):
            pass

    assert "Multiple inheritance" in str(exc_info.value)
    assert "is not allowed" in str(exc_info.value)


def test_get_versions_include_current():
    assert AnotherDerivedClass.get_versions(include_current=True) == [
        DerivedClass,
        AnotherDerivedClass,
    ]


def test_get_versions_no_include_current():
    assert AnotherDerivedClass.get_versions() == [DerivedClass]


def test_next_link_to_object():
    assert DerivedClass._next == AnotherDerivedClass
