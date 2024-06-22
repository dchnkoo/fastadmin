import pydantic as p
import typing as _t


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
