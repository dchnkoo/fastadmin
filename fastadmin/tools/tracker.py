import typing as _t


class InheritanceTracker:
    if _t.TYPE_CHECKING:
        parent: _t.Optional[type["InheritanceTracker"]]

    __define_init_subclass__: bool = True
    __last_version__: type["InheritanceTracker"] = None

    def _init_subclass(cls, alias: str | None = None) -> None:
        parent = cls.__check_multiplie_inheritance__()
        cls.__set_last_version__()
        cls.parent = parent
        cls._check_alias(alias, parent)

    @classmethod
    def _check_alias(
        cls, alias: str | None, parent: type["InheritanceTracker"] | None
    ) -> None:
        if parent is None and alias is not None:
            raise ValueError(
                f"You cannot set alias without parent class ({cls.__name__})"
            )

        if parent is not None and alias is not None:
            if hasattr(parent, alias):
                raise ValueError(
                    f"Alias `{alias}` is already used in `{parent.__name__}`"
                )
            setattr(parent, alias, cls)

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
                "Multiple inheritance with InheritanceTracker object "
                f"is not allowed ({cls.__name__})"
            )

        return parent

    @classmethod
    def get_versions(
        cls, *, include_current: bool = False
    ) -> _t.List[type["InheritanceTracker"]]:
        versions = []
        current = cls.parent
        while current is not None:
            versions.append(current)
            current = current.parent
        versions.reverse()
        if include_current:
            versions.append(cls)
        return versions
