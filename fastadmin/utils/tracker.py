import typing as _t


def inheritance_tracker[_T](obj: type[_T]) -> type[_T]:
    class Wrapper(obj):
        if _t.TYPE_CHECKING:
            _parent: _t.Optional[type[_T]]

        __last_version__: type[_T] = obj

        @classmethod
        def _check_multiple_inheritance(cls) -> _t.Optional[type[_T]]:
            parent = None
            for base in cls.__bases__:
                if base is not Wrapper and issubclass(base, obj):
                    if parent is not None:
                        raise ValueError(
                            f"Multiple inheritance with Page object is not allowed ({cls.__name__})"
                        )
                    parent = base
            return parent

        def __init_subclass__(cls, **kwargs):
            super(Wrapper, cls).__init_subclass__(**kwargs)

            parent = cls._check_multiple_inheritance()
            cls._parent = parent

            if issubclass(cls, cls.__last_version__):
                Wrapper.__last_version__ = cls

        @classmethod
        def get_versions(cls) -> _t.List[type[_T]]:
            versions = []
            current = cls._parent
            while current is not None:
                versions.append(current)
                current = current._parent
            return versions

    return Wrapper
