import typing as _t

if _t.TYPE_CHECKING:
    from starlette.templating import _TemplateResponse
    from fastui import AnyComponent


Template: _t.TypeAlias = "_TemplateResponse"


def inheritance_tracker[_T: "Page"](obj: _t.Type[_T]) -> _t.Type[_T]:
    class Wrapper(obj):
        __pages__ = {}

        @staticmethod
        def _validate_uri(uri: str):
            if isinstance(uri, str) is False:
                raise ValueError("URI must be set")

            if uri.startswith("/") is False:
                raise ValueError("URI must start with a `/`")

        @classmethod
        def _check_multiple_inheritance(cls) -> _t.Optional[type["Page"]]:
            parent = None
            for base in cls.__bases__:
                if base is not Wrapper and issubclass(base, Page):
                    if parent is not None:
                        raise ValueError(
                            f"Multiple inheritance is not allowed ({cls.__name__})"
                        )
                    parent = base
            return parent

        def __init_subclass__(cls, prefix: str = None):
            if prefix is not None:
                if prefix.startswith("/") is False:
                    raise ValueError(f"Prefix must start with a `/` ({cls.__name__})")
                cls._prefix = prefix

            cls._validate_uri(cls.uri)

            if cls.uri in cls.__pages__:
                if issubclass(cls, cls.__pages__[cls.uri]) is False:
                    raise ValueError(
                        f"URI `{cls.uri}` is already used by `{cls.__pages__[cls.uri].__name__}`"
                        f" if you want to use the same URI, please inherit from `{cls.__pages__[cls.uri].__name__}`"
                    )

            cls.__pages__[cls.uri] = cls
            parent = cls._check_multiple_inheritance()
            cls._parent = parent

    return Wrapper


@inheritance_tracker
class Page:
    if _t.TYPE_CHECKING:
        __pages__: _t.Dict[str, type["Page"]]
        _prefix: str
        _parent: _t.Optional[type["Page"]]

    uri: str = ...

    @classmethod
    def page_uri(cls, *, include_parents: bool = False) -> str:
        if include_parents:
            return cls._build_recursive_uri() + cls.uri
        prefix = ""
        if hasattr(cls, "_prefix"):
            prefix = cls._prefix
        return f"{prefix}{cls.uri}"

    @classmethod
    def _get_parents(cls) -> _t.List[type["Page"]]:
        parents = []
        parent = cls._parent

        while parent is not None:
            parents.append(parent)
            parent = parent._parent

        return parents

    @classmethod
    def _page_uris_recursive(cls) -> _t.List[str]:
        return [parent.uri for parent in cls._get_parents()] + [
            cls._prefix if hasattr(cls, "_prefix") else ""
        ]

    @classmethod
    def _build_recursive_uri(cls) -> str:
        uris = cls._page_uris_recursive()
        uris.reverse()
        return "".join(uris)

    def render(self) -> _t.Union[Template, list["AnyComponent"], str]: ...

    def __str__(self):
        return f"<{self.__class__.__name__} {self.page_uri()}>"

    def __repr__(self):
        return self.__str__()

    def __hash__(self):
        return hash(self.page_uri())
