import typing as _t

import pydantic as _p
from fastui import (
    class_name,
    components,
    events,
    types,
)

_T = _t.TypeVar("_T")


if _t.TYPE_CHECKING:

    class CustomizedTable(components.Table, _t.Generic[_T]):
        data: _t.Sequence[_p.SerializeAsAny[_T]]
        data_model: _t.Union[_t.Type[_T], None] = _p.Field(default=None, exclude=True)


class BaseModelComponents(_p.BaseModel):
    if _t.TYPE_CHECKING:
        fast_model_config: _t.ClassVar[_t.Dict[str, _t.Any]]

    @classmethod
    def as_model_form(
        cls,
        submit_url: str,
        initial_data: _t.Dict[str, types.JsonData] | None = None,
        method: _t.Literal["POST", "GOTO", "GET"] = "POST",
        display_mode: _t.Literal["default", "page", "inline"] | None = None,
        submit_on_change: bool | None = None,
        submit_trigger: events.PageEvent | None = None,
        loading: _t.List[components.AnyComponent] | None = None,
        footer: _t.List[components.AnyComponent] | None = None,
        class_name: class_name.ClassNameField | None = None,
    ) -> components.ModelForm:
        """
        Use this method to create a ModelForm component from a Pydantic model.
        """
        return components.ModelForm(
            submit_url=submit_url,
            initial=initial_data,
            method=method,
            display_mode=display_mode,
            submit_on_change=submit_on_change,
            submit_trigger=submit_trigger,
            loading=loading,
            footer=footer,
            class_name=class_name,
            model=cls,
        )

    def as_form(
        self,
        submit_url: str,
        method: _t.Literal["POST", "GOTO", "GET"] = "POST",
        display_mode: _t.Literal["default", "page", "inline"] | None = None,
        submit_on_change: bool | None = None,
        submit_trigger: events.PageEvent | None = None,
        loading: _t.List[components.AnyComponent] | None = None,
        footer: _t.List[components.AnyComponent] | None = None,
        class_name: class_name.ClassNameField | None = None,
        **dump_kwds,
    ) -> components.ModelForm:
        """
        Create a ModelForm component
        from the model instance with initial data from the instance.
        """
        return components.ModelForm(
            submit_url=submit_url,
            initial=self.model_dump(**dump_kwds),
            method=method,
            display_mode=display_mode,
            submit_on_change=submit_on_change,
            submit_trigger=submit_trigger,
            loading=loading,
            footer=footer,
            class_name=class_name,
            model=self.__class__,
        )

    @classmethod
    def as_model_modal_form(
        cls,
        title: str,
        footer: _t.List[components.AnyComponent] | None = None,
        open_trigger: events.PageEvent | None = None,
        open_context: events.ContextType | None = None,
        class_name: class_name.ClassNameField = None,
        **form_kwds: _t.Dict[str, _t.Any],
    ) -> components.Modal:
        """
        Use this method to create a Modal component with a ModelForm inside.
        """
        return components.Modal(
            title=title,
            body=[cls.as_model_form(**form_kwds)],
            footer=footer,
            open_trigger=open_trigger,
            open_context=open_context,
            class_name=class_name,
        )

    def as_modal_form(
        self,
        title: str,
        footer: _t.List[components.AnyComponent] | None = None,
        open_trigger: events.PageEvent | None = None,
        open_context: events.ContextType | None = None,
        class_name: class_name.ClassNameField = None,
        **form_kwds: _t.Dict[str, _t.Any],
    ) -> components.Modal:
        """
        Create a Modal component with a ModelForm inside.
        """
        return components.Modal(
            title=title,
            body=[self.as_form(**form_kwds)],
            footer=footer,
            open_trigger=open_trigger,
            open_context=open_context,
            class_name=class_name,
        )

    def as_details(
        self,
        fields: _t.List[components.display.DisplayLookup | components.display.Display]
        | None = None,
        class_name: class_name.ClassNameField | None = None,
    ) -> components.Details:
        """
        Create a Details component from the model instance.
        """
        return components.Details(
            data=self,
            fields=fields,
            class_name=class_name,
        )

    @classmethod
    def as_model_table(
        cls,
        data: _t.Sequence[_t.Union[_T, _t.Self, dict]],
        columns: _t.List[components.display.DisplayLookup] | None = None,
        no_data_message: str | None = None,
        class_name: class_name.ClassNameField | None = None,
    ) -> "CustomizedTable[_T | _t.Self]":
        """
        Use this method to create a Table component from a Pydantic model.
        """
        from .tools import FastAdminTable, FastBase

        to_table = []

        for item in data:
            if isinstance(item, dict):
                to_table.append(cls(**item))
            elif isinstance(item, (FastBase, FastAdminTable)):
                model = item.to_pydantic_model(**cls.fast_model_config)
                to_table.append(model)
            else:
                to_table.append(item)

        return components.Table(
            data=to_table,
            data_model=cls,
            columns=columns,
            no_data_message=no_data_message,
            class_name=class_name,
        )
