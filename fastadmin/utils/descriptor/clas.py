import typing as _t


class classproperty:
    def __init__(
        self,
        fget: _t.Callable[[_t.Any], _t.Any] | None = None,
        fset: _t.Callable[[_t.Any, _t.Any], None] | None = None,
        fdel: _t.Callable[[_t.Any], None] | None = None,
    ) -> None:
        self.fget = fget
        self.fset = fset
        self.fdel = fdel

    def getter(self, fget: _t.Callable[[_t.Any], _t.Any], /) -> "classproperty":
        self.fget = fget
        return self

    def setter(self, fset: _t.Callable[[_t.Any, _t.Any], None]) -> "classproperty":
        self.fset = fset
        return self

    def deleter(self, fdel: _t.Callable[[_t.Any, _t.Any], None]) -> "classproperty":
        self.fdel = fdel
        return self

    def __get__(self, instance: _t.Any, owner: _t.Optional[type] = None, /):
        if owner is None:
            owner = type(instance)
        if self.fget is None:
            raise AttributeError("unreadable attribute")
        return self.fget(owner)

    def __set__(self, instance: _t.Any, value: _t.Any, /) -> None:
        if self.fset is None:
            raise AttributeError("can't set attribute")
        self.fset(type(instance), value)

    def __delete__(self, instance: _t.Any) -> None:
        if self.fdel is None:
            raise AttributeError("can't delete attribute")
        self.fdel(type(instance))
