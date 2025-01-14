import typing as _t


class InheritanceTracker:
    if _t.TYPE_CHECKING:
        _parent: _t.Optional[type["InheritanceTracker"]]
        _next: _t.Optional[type["InheritanceTracker"]]

    __define_init_subclass__: bool = True
    __last_version__: type["InheritanceTracker"] = None

    def _init_subclass(cls) -> None:
        parent = cls.__check_multiplie_inheritance__()
        cls.__set_last_version__()
        cls._parent = parent
        if parent is not None:
            parent._next = cls

    @classmethod
    def _make_tracker(cls) -> None:
        cls.__main_obj__: type[InheritanceTracker] = cls
        cls.__init_subclass__ = classmethod(cls._init_subclass)

    def __init_subclass__(cls) -> None:
        if cls.__define_init_subclass__ is False:
            return
        cls._make_tracker()

    @classmethod
    def __set_last_version__(cls) -> None:
        main_obj = cls.__main_obj__

        if main_obj.__last_version__ is None:
            main_obj.__last_version__ = cls

        if issubclass(cls, main_obj.__last_version__):
            main_obj.__last_version__ = cls

    @classmethod
    def __check_multiplie_inheritance__(cls) -> _t.Optional[type["InheritanceTracker"]]:
        parent = None
        main_obj = cls.__main_obj__

        same_inheritance_counter = 0
        for base in cls.__bases__:
            if base is not main_obj and issubclass(base, main_obj):
                parent = base

            if issubclass(base, InheritanceTracker):
                same_inheritance_counter += 1

        if same_inheritance_counter > 1:
            raise ValueError(
                f"Multiple inheritance with {InheritanceTracker} object is not allowed ({cls.__name__})"
            )

        return parent

    @classmethod
    def get_versions(
        cls, *, include_current: bool = False
    ) -> _t.List[type["InheritanceTracker"]]:
        versions = []
        current = cls._parent
        while current is not None:
            versions.append(current)
            current = current._parent
        versions.reverse()
        if include_current:
            versions.append(cls)
        return versions
