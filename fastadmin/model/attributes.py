from fastui import components as c, events as e

from fastadmin.utils.descriptor.clas import classproperty

import pydantic as p
import typing as _t

if _t.TYPE_CHECKING:
    from fastadmin.metadata import FastAdminMeta


class ModelAttributes:
    edit_form: _t.Union[p.BaseModel, _t.Dict[str, _t.Any]] = {}
    """
    The attribute determines the appearance of the edit form when adding information to the table.
    The attribute can be left undefined and the model itself will build the edit form by reading your orm sqlalchemy.

    You can configure your edit form using a dictionary in which you specify parameters for the configuration of your model,
    after which the model will build a pydantic BaseModel based on the configuration
    you specified in the dictionary and on your orm model.

    ```python
    from fastadmin.meta import FastAdminMeta

    from fastui.forms import FormFile
    import fastapi as fa

    import pydantic as p
    import typing as _t


    class YourORModel(
        FastAdminMeta,
    ):

        edit_form: dict = {
            "exclude": ["id", "name", ...],
            "fields": {
                "images": (
                    _t.Annotated[
                        _t.List[fa.UploadFile],
                        FormFile("image/*", max_size=16000),
                    ],
                    p.Field(title="Product Images", ...)
                ),
                ...
            },
            "base": SomePydanticBaseModel,
            "validators": {
                "images_validator": p.field_validator("images", mode="before", check_fields=False)(some_function),
            }
        }

    ```

    If you have a pydantic model that reflects your orm model,
    you can specify it directly in this attribute and the model will not read your orm model,
    but will immediately display your pydantic model.

    ```python
    from fastadmin.meta import FastAdminMeta

    from your_project.pydantic_models import MyPydanticModel

    import pydantic as p


    class YourORModel(
        FastAdminMeta,
    ):

        edit_form: p.BaseModel = MyPydanticModel

    ```

    """

    form: _t.Union[p.BaseModel, _t.Dict[str, _t.Any]] = {}
    """
    The attribute determines the appearance of the form when adding information to the table.
    The attribute can be left undefined and the model itself will build the form by reading your orm sqlalchemy.

    You can configure your form using a dictionary in which you specify parameters for the configuration of your model,
    after which the model will build a pydantic BaseModel based on the configuration
    you specified in the dictionary and on your orm model.

    ```python
    from fastadmin.meta import FastAdminMeta

    from fastui.forms import FormFile
    import fastapi as fa

    import pydantic as p
    import typing as _t


    class YourORModel(
        FastAdminMeta,
    ):

        form: dict = {
            "exclude": ["id", "name", ...],
            "fields": {
                "images": (
                    _t.Annotated[
                        _t.List[fa.UploadFile],
                        FormFile("image/*", max_size=16000),
                    ],
                    p.Field(title="Product Images", ...)
                ),
                ...
            },
            "base": SomePydanticBaseModel,
            "validators": {
                "images_validator": p.field_validator("images", mode="before", check_fields=False)(some_function),
            }
        }

    ```

    If you have a pydantic model that reflects your orm model,
    you can specify it directly in this attribute and the model will not read your orm model,
    but will immediately display your pydantic model.

    ```python
    from fastadmin.meta import FastAdminMeta

    from your_project.pydantic_models import MyPydanticModel

    import pydantic as p


    class YourORModel(
        FastAdminMeta,
    ):

        form: p.BaseModel = MyPydanticModel

    ```

    """

    admin: _t.Union[p.BaseModel, _t.Dict[str, _t.Any]] = {}
    """
    The attribute determines the appearance of the admin when adding information to the table.
    The attribute can be left undefined and the model itself will build the admin by reading your orm sqlalchemy.

    You can configure your admin using a dictionary in which you specify parameters for the configuration of your model,
    after which the model will build a pydantic BaseModel based on the configuration
    you specified in the dictionary and on your orm model.

    ```python
    from fastadmin.meta import FastAdminMeta

    from fastui.forms import FormFile
    import fastapi as fa

    import pydantic as p
    import typing as _t


    class YourORModel(
        FastAdminMeta,
    ):

        admin: dict = {
            "exclude": ["id", "name", ...],
            "fields": {
                "images": (
                    _t.Annotated[
                        _t.List[fa.UploadFile],
                        FormFile("image/*", max_size=16000),
                    ],
                    p.Field(title="Product Images", ...)
                ),
                ...
            },
            "base": SomePydanticBaseModel,
            "validators": {
                "images_validator": p.field_validator("images", mode="before", check_fields=False)(some_function),
            }
        }

    ```

    If you have a pydantic model that reflects your orm model,
    you can specify it directly in this attribute and the model will not read your orm model,
    but will immediately display your pydantic model.

    ```python
    from fastadmin.meta import FastAdminMeta

    from your_project.pydantic_models import MyPydanticModel

    import pydantic as p


    class YourORModel(
        FastAdminMeta,
    ):

        admin: p.BaseModel = MyPydanticModel

    ```

    """

    repr: _t.Union[p.BaseModel, _t.Dict[str, _t.Any]] = {}
    """
    The attribute determines the appearance of the repr when adding information to the table.
    The attribute can be left undefined and the model itself will build the repr by reading your orm sqlalchemy.

    You can configure your repr using a dictionary in which you specify parameters for the configuration of your model,
    after which the model will build a pydantic BaseModel based on the configuration
    you specified in the dictionary and on your orm model.

    ```python
    from fastadmin.meta import FastAdminMeta

    from fastui.forms import FormFile
    import fastapi as fa

    import pydantic as p
    import typing as _t


    class YourORModel(
        FastAdminMeta,
    ):

        repr: dict = {
            "exclude": ["id", "name", ...],
            "fields": {
                "images": (
                    _t.Annotated[
                        _t.List[fa.UploadFile],
                        FormFile("image/*", max_size=16000),
                    ],
                    p.Field(title="Product Images", ...)
                ),
                ...
            },
            "base": SomePydanticBaseModel,
            "validators": {
                "images_validator": p.field_validator("images", mode="before", check_fields=False)(some_function),
            }
        }

    ```

    If you have a pydantic model that reflects your orm model,
    you can specify it directly in this attribute and the model will not read your orm model,
    but will immediately display your pydantic model.

    ```python
    from fastadmin.meta import FastAdminMeta

    from your_project.pydantic_models import MyPydanticModel

    import pydantic as p


    class YourORModel(
        FastAdminMeta,
    ):

        repr: p.BaseModel = MyPydanticModel

    ```
    """

    can_add: bool = True
    """
    If the attribute is True, then it will be possible to add data from the admin panel to the table.

    default is True.
    """

    can_delete: bool = True
    """
    If the attribute is True, then it will be possible to delete data from the admin panel in the table.

    default is True.
    """

    can_edit: bool = True
    """
    If the attribute is True, then it will be possible to edit data from the admin panel in the table.

    default is True.
    """

    @classproperty
    def display_lookups(cls: "FastAdminMeta") -> list[c.display.DisplayLookup]:
        """
        List of :object:`DisplayLookup` implement this list to
        configure which columns to show on page of this table.
        """
        lookups: list[c.display.DisplayLookup] = []

        meta = cls.__get_metainfo__(cls.__tablename__)

        if meta.unique_columns:
            column = list(meta.unique_columns.keys())[0]

            url = f"./{column}" + "/{" + column + "}"

            lookups.append(
                c.display.DisplayLookup(field=column, on_click=e.GoToEvent(url=url))
            )

        else:
            column = list(meta.primary_columns.keys())[0]

            url = f"./{column}" + "/{" + column + "}"

            lookups.append(
                c.display.DisplayLookup(field=column, on_click=e.GoToEvent(url=url))
            )

        for column in meta.columns:
            if column != lookups[0].field:
                lookups.append(c.display.DisplayLookup(field=column))

        return lookups

    table_size: int = 25
    """
    Size of data on the page for this table.
    """

    __title__: _t.Optional[str] = None
    """
    title for this table which will be used anywhere in admin UI.
    """

    no_data_message: _t.Optional[str] = None
    """
    if not data in table this message will be display on page.
    """

    hide_in_link: bool = False
    """
    if value is True it doesn't will be shows in table links
    """
