from .tracker import InheritanceTracker

from sqlalchemy.util import FacadeDict

from fastui import AnyComponent, components, events, auth as _auth

from fastapi import responses

import typing as _t
import inspect
import enum

if _t.TYPE_CHECKING:
    from starlette.templating import _TemplateResponse
    from .tools import FastAdminTable


Template: _t.TypeAlias = "_TemplateResponse"


SPECIFIC_TYPES = (
    list["AnyComponent"],
    "list[AnyComponent]",
    list[AnyComponent],
)


FASTAPI_RESPONSES = tuple(
    fresponse
    for response in inspect.getmembers(responses, inspect.isclass)
    if issubclass((fresponse := response[1]), responses.Response)
    or fresponse is responses.Response
)


ALLOWED_RESPONSES = SPECIFIC_TYPES + FASTAPI_RESPONSES


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

    root_url: str = ""
    path_strip: str = ""
    mount_path: str = ""

    def __init__(self):
        self.__pages__: _t.Dict[str, type["Page"]] = {}


class Page(InheritanceTracker):
    if _t.TYPE_CHECKING:
        __main_obj__: type["Page"]
        _type: type
        parent: _t.Optional[type["Page"]]
        __pages__: _t.Dict[str, type["Page"]]

        @classmethod
        def get_versions(
            cls, *, include_current: bool = False
        ) -> _t.List[type["Page"]]: ...
        def render(self) -> _t.Union[Template, list["AnyComponent"], str, dict]: ...

    comp = components
    display = components.display
    event = events
    auth = _auth

    _prefix: str = ""
    __define_init_subclass__ = False
    __pagemeta__ = PageMeta()
    method: RestMethods = RestMethods.GET
    uri: str = ...

    def _init_subclass(cls, prefix: str = None, alias: str | None = None):
        super(Page, cls)._init_subclass(cls, alias)
        if prefix is not None:
            if prefix.startswith("/") is False:
                raise ValueError(f"Prefix must start with a `/` ({cls.__name__})")
            cls._prefix = prefix

        cls._validate_uri(cls.uri)

        if cls.uri in cls.__pages__:
            pages = cls.__pages__
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
        cls.__check_metdata__()
        cls.__pages__ = cls.__pagemeta__.__pages__
        cls._make_tracker()

    @classmethod
    def __check_metdata__(cls):
        metadata = cls.__pagemeta__

        if type(metadata) is type:
            raise ValueError(f"{metadata} need to be an instance")

        if (type(metadata) is PageMeta) is False:
            if issubclass(type(metadata), PageMeta) is False:
                raise ValueError(f"You need to specify `__pagemeta__` for {cls}")

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

        if return_annotation not in ALLOWED_RESPONSES:
            raise ValueError(
                f"Page `render` method must return one of {ALLOWED_RESPONSES} ({cls.__name__})"
            )

        return return_annotation

    @classmethod
    def get_uri(cls, *args, add_root_uri: bool = True, **kwds) -> str:
        if add_root_uri is False:
            root_prefix = cls.__pagemeta__.path_strip
        else:
            root_prefix = cls.__pagemeta__.root_url

        uri = (
            cls.__pagemeta__.mount_path
            + root_prefix
            + cls._build_recursive_uri()
            + cls.uri
        )

        if args or kwds:
            return uri.format(*args, **kwds)
        return uri

    @classmethod
    def _page_uris_recursive(cls) -> _t.List[str]:
        return [parent.uri for parent in cls.get_versions()]

    @classmethod
    def _build_recursive_uri(cls) -> str:
        uris = cls._page_uris_recursive()
        return cls._prefix + "".join(uris)

    def __str__(self):
        return f"<{self.__class__.__name__} {self.get_uri()}>"

    def __repr__(self):
        return self.__str__()

    def __hash__(self):
        return hash(self.uri)
