from .tracker import InheritanceTracker

from sqlalchemy.util import FacadeDict

from fastui import AnyComponent

import typing as _t
import inspect
import enum

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


class UriType(enum.StrEnum):
    URI = "uri"
    WITH_PREFIX = "with_prefix"
    WITH_PARENTS = "with_parents"


class RestMethods(enum.StrEnum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    OPTIONS = "OPTIONS"
    HEAD = "HEAD"
    TRACE = "TRACE"


class PageMeta:
    if _t.TYPE_CHECKING:
        _tables: FacadeDict[str, "FastAdminTable"]

    __pages__: _t.Dict[str, type["Page"]] = {}

    def __new__(cls):
        if hasattr(cls, "instance") is False:
            cls.instance = super(PageMeta, cls).__new__(cls)
        return cls.instance


class Page(InheritanceTracker):
    if _t.TYPE_CHECKING:
        __main_obj__: _t.Callable[[], type["Page"]]
        _prefix: str
        _type: type
        router_prefix: str
        _parent: _t.Optional[type["Page"]]
        _next: _t.Optional[type["Page"]]

        @classmethod
        def get_versions(cls) -> _t.List[type["Page"]]: ...
        def render(self) -> _t.Union[Template, list["AnyComponent"], str]: ...

    __define_init_subclass__ = False
    __pagemeta__ = PageMeta()
    __pages__ = lambda: Page.__pagemeta__.__pages__  # noqa E731
    method: RestMethods = RestMethods.GET
    uri_type: UriType = UriType.URI
    uri: str = ...

    def _init_subclass(cls, prefix: str = None):
        super(Page, cls)._init_subclass(cls)
        if prefix is not None:
            if prefix.startswith("/") is False:
                raise ValueError(f"Prefix must start with a `/` ({cls.__name__})")
            cls._prefix = prefix

        cls._validate_uri(cls.uri)

        if cls.uri in cls.__pages__():
            pages = cls.__pages__()
            if issubclass(cls, pages[cls.uri]) is False:
                raise ValueError(
                    f"URI `{cls.uri}` is already used by `{pages[cls.uri].__name__}`"
                    f" if you want to use the same URI, please inherit from `{pages[cls.uri].__name__}`"
                )

        cls._set_page()
        page_type = cls._validate_render_func()
        cls._type = page_type

        if cls.method not in RestMethods:
            raise ValueError(f"Method must be one of {RestMethods} ({cls.__name__})")

    def __init_subclass__(cls):
        cls._make_tracker()

    @classmethod
    def _set_page(cls):
        cls.__pagemeta__.__pages__[cls.get_uri()] = cls

    @staticmethod
    def _validate_uri(uri: str):
        if isinstance(uri, str) is False:
            raise ValueError("URI must be set")

        if uri.startswith("/") is False:
            raise ValueError("URI must start with a `/`")

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

    @classmethod
    def router_url(cls) -> str:
        return cls.router_prefix + cls.get_uri()

    @classmethod
    def get_uri(cls) -> str:
        return cls._handle_uri_type()

    @classmethod
    def _handle_uri_type(cls) -> str:
        match cls.uri_type:
            case UriType.URI:
                return cls.uri
            case UriType.WITH_PREFIX:
                return cls._page_uri()
            case UriType.WITH_PARENTS:
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
        return [parent.uri for parent in cls.get_versions()] + [
            cls._prefix if hasattr(cls, "_prefix") else ""
        ]

    @classmethod
    def _build_recursive_uri(cls) -> str:
        uris = cls._page_uris_recursive()
        uris.reverse()
        return "".join(uris)

    def __str__(self):
        return f"<{self.__class__.__name__} {self._page_uri()}>"

    def __repr__(self):
        return self.__str__()

    def __hash__(self):
        return hash(self._page_uri())
