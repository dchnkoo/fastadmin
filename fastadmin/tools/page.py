from sqlalchemy.util import FacadeDict

from fastui import AnyComponent

import typing as _t
import inspect

if _t.TYPE_CHECKING:
    from starlette.templating import _TemplateResponse
    from .tools import FastAdminTable


Template: _t.TypeAlias = "_TemplateResponse"


ALLOWED_RETURN_TYPES = (
    list["AnyComponent"],
    "list[AnyComponent]",
    list[AnyComponent],
    "Template",
    Template,
    str,
)


URI_TYPE = _t.Literal["uri", "with_prefix", "with_parents"]


API_METHODS = _t.Literal[
    "GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD", "TRACE"
]


def inheritance_page_tracker[_T: "Page"](obj: _t.Type[_T]) -> _t.Type[_T]:
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
                            f"Multiple inheritance with Page object is not allowed ({cls.__name__})"
                        )
                    parent = base
            return parent

        @classmethod
        def _validate_render_func(cls):
            funcs = inspect.getmembers_static(cls, predicate=inspect.isfunction)
            render_func = dict(funcs).get("render")

            if render_func is None:
                raise ValueError(f"Page must have a `render` method ({cls.__name__})")

            splited_name = render_func.__qualname__.split(".")
            index = splited_name.index("render")
            object_name = splited_name[index - 1]

            if object_name != cls.__name__:
                raise ValueError(
                    f"Page `render` method must be a method of the class ({cls.__name__})"
                )

            func_signature = inspect.signature(render_func)

            return_annotation = func_signature.return_annotation
            if return_annotation == func_signature.empty:
                raise ValueError(
                    f"Page `render` method must have a return annotation ({cls.__name__})"
                )

            if return_annotation not in ALLOWED_RETURN_TYPES:
                raise ValueError(
                    f"Page `render` method must return one of {ALLOWED_RETURN_TYPES} ({cls.__name__})"
                )

            return return_annotation

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

            if cls.abstract is False:
                cls.__pages__[cls.get_uri()] = cls
            parent = cls._check_multiple_inheritance()
            cls._parent = parent

            page_type = cls._validate_render_func()
            cls._type = page_type

            if cls.method not in _t.get_args(API_METHODS):
                raise ValueError(
                    f"Method must be one of {API_METHODS} ({cls.__name__})"
                )

    return Wrapper


@inheritance_page_tracker
class Page:
    if _t.TYPE_CHECKING:
        __pages__: _t.Dict[str, type["Page"]]
        _prefix: str
        _parent: _t.Optional[type["Page"]]
        _type: type
        _tables: FacadeDict[str, "FastAdminTable"]

    abstract: bool = False
    method: API_METHODS = "GET"
    uri_type: URI_TYPE = "uri"
    uri: str = ...

    @classmethod
    def _get_parents(cls) -> _t.List[type["Page"]]:
        parents = []
        parent = cls._parent

        while parent is not None:
            parents.append(parent)
            parent = parent._parent

        return parents

    @classmethod
    def get_uri(cls) -> str:
        return cls._handle_uri_type()

    @classmethod
    def _handle_uri_type(cls) -> str:
        if cls.uri_type == "uri":
            return cls.uri
        elif cls.uri_type == "with_prefix":
            return cls._page_uri()
        elif cls.uri_type == "with_parents":
            return cls._page_uri(include_parents=True)

    @classmethod
    def _page_uri(cls, *, include_parents: bool = False) -> str:
        if include_parents:
            return cls._build_recursive_uri() + cls.uri
        prefix = ""
        if hasattr(cls, "_prefix"):
            prefix = cls._prefix
        return f"{prefix}{cls.uri}"

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
        return f"<{self.__class__.__name__} {self._page_uri()}>"

    def __repr__(self):
        return self.__str__()

    def __hash__(self):
        return hash(self._page_uri())
