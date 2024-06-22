import sqlalchemy as sa

from pydantic_core import PydanticUndefined
import pydantic as p

import typing as _t


class SQLModel2Pydantic:
    @classmethod
    def which_model(
        cls,
        model: sa.Table,
        model_type: _t.Literal["form", "edit_form", "admin", "repr"] = "repr",
    ):
        config_dict: p.BaseModel | dict = getattr(model, model_type)

        if hasattr(config_dict, "__pydantic_root_model__"):
            return config_dict

        exclude = config_dict.get("exclude", [])
        fields = config_dict.get("fields", {})
        validators = config_dict.get("validators", None)
        base = config_dict.get("base", None)

        return cls.generate_pydantic_model(
            model=model,
            exclude=exclude,
            fields=fields,
            validators=validators,
            base=base,
        )

    @staticmethod
    def generate_pydantic_model(
        model: sa.Table,
        exclude: list[str],
        fields: dict,
        validators: dict[str, classmethod] | None,
        base: p.BaseModel | None,
    ) -> p.BaseModel:
        config_dict = {}

        config_dict["__model_name"] = model.__name__

        fields_list = list(fields.keys())
        columns = [
            column.name
            for column in model.__table__.columns
            if column.name not in fields_list
        ]
        columns.extend(fields_list)

        for column in columns:
            if column not in exclude:
                field = fields.get(column, None)
                if field:
                    config_dict[column] = field
                    continue

                model_column: sa.Column = getattr(model, column)
                python_type = model_column.type.python_type

                config_dict[column] = (
                    _t.Optional[python_type] if model_column.nullable else python_type,
                    p.Field(
                        default=None
                        if (
                            model_column.nullable is True
                            and model_column.default is None
                        )
                        else PydanticUndefined
                        if model_column.default is None
                        else model_column.default.arg,
                        title=model_column.doc,
                    ),
                )

        return p.create_model(__base__=base, __validators__=validators, **config_dict)
