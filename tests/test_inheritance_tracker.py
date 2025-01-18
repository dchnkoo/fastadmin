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
    assert DerivedClass.parent == None
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


def test_alias_without_parent():
    with pytest.raises(ValueError) as exc_info:

        class InitTracker(InheritanceTracker):
            pass

        class AliasWithoutParent(InitTracker, alias="alias"):
            pass

    assert "You cannot set alias without parent class" in str(exc_info.value)


def test_alias_with_parent():
    class InitTracker(InheritanceTracker):
        pass

    class ParentClass(InitTracker):
        pass

    class ChildClass(ParentClass, alias="child"):
        pass

    assert hasattr(ParentClass, "child")
    assert ParentClass.child == ChildClass


def test_duplicate_alias():
    class InitTracker(InheritanceTracker):
        pass

    class ParentClass(InitTracker):
        pass

    class FirstChildClass(ParentClass, alias="child"):
        pass

    with pytest.raises(ValueError) as exc_info:

        class SecondChildClass(ParentClass, alias="child"):
            pass

    assert "Alias `child` is already used in `ParentClass`" in str(exc_info.value)
