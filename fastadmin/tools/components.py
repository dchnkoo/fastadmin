from fastui import (
    class_name as _cs,
    components as _c,
    events as _e,
    types,
)

import pydantic as _p
import typing as _t

if _t.TYPE_CHECKING:
    from .tools import FastAdminBase


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
        submit_trigger: _e.PageEvent | None = None,
        loading: _t.List[_c.AnyComponent] | None = None,
        footer: _t.List[_c.AnyComponent] | None = None,
        class_name: _cs.ClassNameField | None = None,
    ) -> _c.ModelForm:
        """
        Use this method to create a ModelForm component from a Pydantic model.
        """
        return _c.ModelForm(
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
        submit_trigger: _e.PageEvent | None = None,
        loading: _t.List[_c.AnyComponent] | None = None,
        footer: _t.List[_c.AnyComponent] | None = None,
        class_name: _cs.ClassNameField | None = None,
        **dump_kwds,
    ) -> _c.ModelForm:
        """
        Create a ModelForm component from the model instance with initial data from the instance.
        """
        return _c.ModelForm(
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
        footer: _t.List[_c.AnyComponent] | None = None,
        open_trigger: _e.PageEvent | None = None,
        open_context: _e.ContextType | None = None,
        class_name: _cs.ClassNameField = None,
        **form_kwds: _t.Dict[str, _t.Any],
    ) -> _c.Modal:
        """
        Use this method to create a Modal component with a ModelForm inside.
        """
        return _c.Modal(
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
        footer: _t.List[_c.AnyComponent] | None = None,
        open_trigger: _e.PageEvent | None = None,
        open_context: _e.ContextType | None = None,
        class_name: _cs.ClassNameField = None,
        **form_kwds: _t.Dict[str, _t.Any],
    ) -> _c.Modal:
        """
        Create a Modal component with a ModelForm inside.
        """
        return _c.Modal(
            title=title,
            body=[self.as_form(**form_kwds)],
            footer=footer,
            open_trigger=open_trigger,
            open_context=open_context,
            class_name=class_name,
        )

    def as_details(
        self,
        fields: _t.List[_c.display.DisplayLookup | _c.display.Display] | None = None,
        class_name: _cs.ClassNameField | None = None,
    ) -> _c.Details:
        """
        Create a Details component from the model instance.
        """
        return _c.Details(
            data=self,
            fields=fields,
            class_name=class_name,
        )

    @classmethod
    def as_model_table(
        cls,
        data: _t.Sequence[_t.Union["FastAdminBase", _t.Self, dict]],
        columns: _t.List[_c.display.DisplayLookup] | None = None,
        no_data_message: str | None = None,
        class_name: _cs.ClassNameField | None = None,
    ) -> _c.Table:
        """
        Use this method to create a Table component from a Pydantic model.
        """
        from .tools import FastAdminBase, FastAdminTable

        to_table = []

        for item in data:
            if isinstance(item, dict):
                to_table.append(cls(**item))
            elif isinstance(item, (FastAdminBase, FastAdminTable)):
                model = item.to_pydantic_model(**cls.fast_model_config)
                to_table.append(model)
            else:
                to_table.append(item)

        return _c.Table(
            data=to_table,
            data_model=cls,
            columns=columns,
            no_data_message=no_data_message,
            class_name=class_name,
        )
